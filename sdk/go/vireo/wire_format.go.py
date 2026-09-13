package vireo

import (
    "bytes"
    "encoding/binary"
    "encoding/json"
    "fmt"
    "time"
)

// ============================================================
// WIRE FORMAT CONSTANTS
// ============================================================

const (
    WireMagic   uint32 = 0x56495245 // 'VIRE' in hex
    WireVersion uint32 = 0x03000000 // v3.0.0
    WireHeaderSize      = 16        // bytes
)

// ============================================================
// WIRE FORMAT
// ============================================================

type WireHeader struct {
    Magic       uint32
    Version     uint32
    MessageType uint32
    Flags       uint32
    BodyLength  uint32
}

type WireFormat struct{}

// ============================================================
// SERIALIZATION
// ============================================================

func (w *WireFormat) Serialize(envelope *MessageEnvelope) ([]byte, error) {
    headerBytes, err := w.serializeHeader(&envelope.Header)
    if err != nil {
        return nil, err
    }

    var bodyBytes []byte
    if envelope.Body != nil {
        bodyBytes, err = w.serializeBody(envelope.Body)
        if err != nil {
            return nil, err
        }
    }

    result := make([]byte, len(headerBytes)+len(bodyBytes))
    copy(result[:len(headerBytes)], headerBytes)
    copy(result[len(headerBytes):], bodyBytes)

    return result, nil
}

func (w *WireFormat) Deserialize(data []byte) (*MessageEnvelope, error) {
    if len(data) < WireHeaderSize {
        return nil, NewSerializationError("Data too short for wire format", "")
    }

    header, bodyStart, err := w.deserializeHeader(data)
    if err != nil {
        return nil, err
    }

    bodyEnd := bodyStart + int(header.BodyLength)
    if len(data) < bodyEnd {
        return nil, NewSerializationError("Data too short for body", "")
    }

    bodyData := data[bodyStart:bodyEnd]
    body, err := w.deserializeBody(bodyData, header.MessageType)
    if err != nil {
        return nil, err
    }

    envelope := &MessageEnvelope{
        Header: *header,
        Body:   body,
    }

    return envelope, nil
}

// ============================================================
// HEADER SERIALIZATION
// ============================================================

func (w *WireFormat) serializeHeader(header *MessageHeader) ([]byte, error) {
    buf := new(bytes.Buffer)

    // Magic number
    if err := binary.Write(buf, binary.BigEndian, WireMagic); err != nil {
        return nil, err
    }

    // Version
    if err := binary.Write(buf, binary.BigEndian, WireVersion); err != nil {
        return nil, err
    }

    // Message type
    typeMap := map[MessageType]uint32{
        MsgPropose:  1,
        MsgCommit:   2,
        MsgExecute:  3,
        MsgVerify:   4,
        MsgEscalate: 5,
        MsgDone:     6,
        MsgFailed:   7,
        MsgTimeout:  8,
        MsgAck:      9,
        MsgNack:     10,
        MsgQuery:    11,
        MsgResponse: 12,
        MsgError:    13,
    }
    typeCode := typeMap[header.Type]
    if err := binary.Write(buf, binary.BigEndian, typeCode); err != nil {
        return nil, err
    }

    // Flags
    var flags uint32 = 0
    if header.Signature != nil {
        flags |= 0x01
    }
    if header.Nonce != nil {
        flags |= 0x02
    }
    if header.Receiver != nil {
        flags |= 0x04
    }
    if header.CorrelationID != nil {
        flags |= 0x08
    }
    if header.ReplyTo != nil {
        flags |= 0x10
    }
    if err := binary.Write(buf, binary.BigEndian, flags); err != nil {
        return nil, err
    }

    return buf.Bytes(), nil
}

func (w *WireFormat) deserializeHeader(data []byte) (*MessageHeader, int, error) {
    buf := bytes.NewReader(data)

    var magic uint32
    if err := binary.Read(buf, binary.BigEndian, &magic); err != nil {
        return nil, 0, err
    }
    if magic != WireMagic {
        return nil, 0, NewSerializationError(fmt.Sprintf("Invalid magic number: %x", magic), "")
    }

    var version uint32
    if err := binary.Read(buf, binary.BigEndian, &version); err != nil {
        return nil, 0, err
    }

    var typeCode uint32
    if err := binary.Read(buf, binary.BigEndian, &typeCode); err != nil {
        return nil, 0, err
    }

    var flags uint32
    if err := binary.Read(buf, binary.BigEndian, &flags); err != nil {
        return nil, 0, err
    }

    typeMap := map[uint32]MessageType{
        1:  MsgPropose,
        2:  MsgCommit,
        3:  MsgExecute,
        4:  MsgVerify,
        5:  MsgEscalate,
        6:  MsgDone,
        7:  MsgFailed,
        8:  MsgTimeout,
        9:  MsgAck,
        10: MsgNack,
        11: MsgQuery,
        12: MsgResponse,
        13: MsgError,
    }

    msgType := typeMap[typeCode]
    if msgType == "" {
        msgType = MsgError
    }

    header := &MessageHeader{
        Type:       msgType,
        Version:    fmt.Sprintf("%d.%d.%d", (version>>24)&0xFF, (version>>16)&0xFF, (version>>8)&0xFF),
        MessageID:  generateUUID(),
        Timestamp:  time.Now().UTC(),
        Sender:     "",
        TTLSeconds: 300,
        Priority:   0,
        Flags:      []string{},
    }

    if flags&0x01 != 0 {
        sig := "placeholder"
        header.Signature = &sig
    }
    if flags&0x02 != 0 {
        nonce := "placeholder"
        header.Nonce = &nonce
    }
    if flags&0x04 != 0 {
        recv := "placeholder"
        header.Receiver = &recv
    }
    if flags&0x08 != 0 {
        corr := "placeholder"
        header.CorrelationID = &corr
    }
    if flags&0x10 != 0 {
        reply := "placeholder"
        header.ReplyTo = &reply
    }

    bodyStart := int(buf.Size())
    return header, bodyStart, nil
}

// ============================================================
// BODY SERIALIZATION
// ============================================================

func (w *WireFormat) serializeBody(body *MessageBody) ([]byte, error) {
    data := map[string]interface{}{
        "content_type": body.ContentType,
        "data":         w.serializeValue(&body.Data),
        "metadata":     body.Metadata,
    }
    if body.SchemaURI != nil {
        data["schema_uri"] = *body.SchemaURI
    }

    jsonData, err := json.Marshal(data)
    if err != nil {
        return nil, err
    }

    return jsonData, nil
}

func (w *WireFormat) deserializeBody(data []byte, messageType uint32) (*MessageBody, error) {
    if len(data) == 0 {
        return nil, nil
    }

    var parsed map[string]interface{}
    if err := json.Unmarshal(data, &parsed); err != nil {
        return nil, err
    }

    contentType := "application/json"
    if ct, ok := parsed["content_type"].(string); ok {
        contentType = ct
    }

    var schemaURI *string
    if uri, ok := parsed["schema_uri"].(string); ok {
        schemaURI = &uri
    }

    metadata := map[string]interface{}{}
    if meta, ok := parsed["metadata"].(map[string]interface{}); ok {
        metadata = meta
    }

    var value VireoValue
    if dataVal, ok := parsed["data"]; ok {
        value = w.deserializeValue(dataVal)
    }

    body := &MessageBody{
        ContentType: contentType,
        Data:        value,
        Metadata:    metadata,
        SchemaURI:   schemaURI,
        Size:        len(data),
    }

    return body, nil
}

// ============================================================
// VALUE SERIALIZATION
// ============================================================

func (w *WireFormat) serializeValue(value *VireoValue) interface{} {
    if value == nil {
        return nil
    }

    switch value.Type {
    case TypeNull:
        return nil
    case TypeBoolean:
        return value.Value
    case TypeInteger:
        return value.Value
    case TypeFloat:
        return value.Value
    case TypeString:
        return value.Value
    case TypeBinary:
        if bytes, ok := value.Value.([]byte); ok {
            return map[string]interface{}{
                "__type":  "binary",
                "value":   fmt.Sprintf("%x", bytes),
            }
        }
    case TypeArray:
        if arr, ok := value.Value.([]VireoValue); ok {
            result := make([]interface{}, len(arr))
            for i, v := range arr {
                result[i] = w.serializeValue(&v)
            }
            return result
        }
    case TypeObject:
        if obj, ok := value.Value.(VireoObject); ok {
            result := make(map[string]interface{})
            for k, v := range obj {
                result[k] = w.serializeValue(&v)
            }
            return result
        }
    case TypeTimestamp:
        if t, ok := value.Value.(time.Time); ok {
            return map[string]interface{}{
                "__type": "timestamp",
                "value":  t.Format(time.RFC3339Nano),
            }
        }
    case TypeDID:
        if did, ok := value.Value.(string); ok {
            return map[string]interface{}{
                "__type": "did",
                "value":  did,
            }
        }
    case TypeSignature:
        if sig, ok := value.Value.([]byte); ok {
            return map[string]interface{}{
                "__type": "signature",
                "value":  fmt.Sprintf("%x", sig),
            }
        }
    case TypeNonce:
        if nonce, ok := value.Value.([]byte); ok {
            return map[string]interface{}{
                "__type": "nonce",
                "value":  fmt.Sprintf("%x", nonce),
            }
        }
    default:
        return value.Value
    }

    return value.Value
}

func (w *WireFormat) deserializeValue(data interface{}) VireoValue {
    if data == nil {
        return VireoValue{Type: TypeNull, Value: nil}
    }

    switch v := data.(type) {
    case bool:
        return VireoValue{Type: TypeBoolean, Value: v}
    case float64:
        if float64(int64(v)) == v {
            return VireoValue{Type: TypeInteger, Value: int64(v)}
        }
        return VireoValue{Type: TypeFloat, Value: v}
    case string:
        return VireoValue{Type: TypeString, Value: v}
    case []interface{}:
        arr := make([]VireoValue, len(v))
        for i, item := range v {
            arr[i] = w.deserializeValue(item)
        }
        return VireoValue{Type: TypeArray, Value: arr}
    case map[string]interface{}:
        if typ, ok := v["__type"].(string); ok {
            switch typ {
            case "binary":
                if hex, ok := v["value"].(string); ok {
                    bytes, _ := hexToBytes(hex)
                    return VireoValue{Type: TypeBinary, Value: bytes}
                }
            case "timestamp":
                if ts, ok := v["value"].(string); ok {
                    if t, err := time.Parse(time.RFC3339Nano, ts); err == nil {
                        return VireoValue{Type: TypeTimestamp, Value: t}
                    }
                }
            case "did":
                if did, ok := v["value"].(string); ok {
                    return VireoValue{Type: TypeDID, Value: did}
                }
            case "signature":
                if hex, ok := v["value"].(string); ok {
                    bytes, _ := hexToBytes(hex)
                    return VireoValue{Type: TypeSignature, Value: bytes}
                }
            case "nonce":
                if hex, ok := v["value"].(string); ok {
                    bytes, _ := hexToBytes(hex)
                    return VireoValue{Type: TypeNonce, Value: bytes}
                }
            }
        }

        obj := make(VireoObject)
        for k, val := range v {
            obj[k] = w.deserializeValue(val)
        }
        return VireoValue{Type: TypeObject, Value: obj}
    default:
        return VireoValue{Type: TypeNull, Value: nil}
    }
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

func (w *WireFormat) IsValid(data []byte) bool {
    if len(data) < WireHeaderSize {
        return false
    }
    magic := binary.BigEndian.Uint32(data[:4])
    return magic == WireMagic
}

func generateUUID() string {
    return fmt.Sprintf("%x-%x-%x-%x-%x",
        uint32(randInt()),
        uint16(randInt()),
        uint16(randInt()),
        uint16(randInt()),
        uint32(randInt()))
}

func randInt() uint64 {
    return uint64(time.Now().UnixNano()) & 0xFFFFFFFF
}

func hexToBytes(hex string) ([]byte, error) {
    if len(hex)%2 != 0 {
        return nil, fmt.Errorf("invalid hex string: odd length")
    }
    result := make([]byte, len(hex)/2)
    for i := 0; i < len(hex); i += 2 {
        var b byte
        if _, err := fmt.Sscanf(hex[i:i+2], "%02x", &b); err != nil {
            return nil, err
        }
        result[i/2] = b
    }
    return result, nil
}