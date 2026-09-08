package com.vireo;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * Vireo Wire Format Serialization
 * 
 * Binary canonical format for Vireo messages
 */
public class WireFormat {

    private static final int WIRE_MAGIC = 0x56495245; // 'VIRE'
    private static final int WIRE_VERSION = 0x03000000; // v3.0.0
    private static final int WIRE_HEADER_SIZE = 16;

    private static final ObjectMapper objectMapper = new ObjectMapper()
            .registerModule(new JavaTimeModule())
            .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);

    private static final Map<Types.MessageType, Integer> TYPE_MAP = new HashMap<>();
    private static final Map<Integer, Types.MessageType> TYPE_REVERSE_MAP = new HashMap<>();

    static {
        TYPE_MAP.put(Types.MessageType.PROPOSE, 1);
        TYPE_MAP.put(Types.MessageType.COMMIT, 2);
        TYPE_MAP.put(Types.MessageType.EXECUTE, 3);
        TYPE_MAP.put(Types.MessageType.VERIFY, 4);
        TYPE_MAP.put(Types.MessageType.ESCALATE, 5);
        TYPE_MAP.put(Types.MessageType.DONE, 6);
        TYPE_MAP.put(Types.MessageType.FAILED, 7);
        TYPE_MAP.put(Types.MessageType.TIMEOUT, 8);
        TYPE_MAP.put(Types.MessageType.ACK, 9);
        TYPE_MAP.put(Types.MessageType.NACK, 10);
        TYPE_MAP.put(Types.MessageType.QUERY, 11);
        TYPE_MAP.put(Types.MessageType.RESPONSE, 12);
        TYPE_MAP.put(Types.MessageType.ERROR, 13);

        for (Map.Entry<Types.MessageType, Integer> entry : TYPE_MAP.entrySet()) {
            TYPE_REVERSE_MAP.put(entry.getValue(), entry.getKey());
        }
    }

    /**
     * Serialize a message envelope to binary format
     */
    public static byte[] serialize(Types.MessageEnvelope envelope) throws Errors.SerializationException {
        try {
            byte[] headerBytes = serializeHeader(envelope.getHeader());
            byte[] bodyBytes = envelope.getBody() != null ? serializeBody(envelope.getBody()) : new byte[0];

            byte[] result = new byte[headerBytes.length + bodyBytes.length];
            System.arraycopy(headerBytes, 0, result, 0, headerBytes.length);
            System.arraycopy(bodyBytes, 0, result, headerBytes.length, bodyBytes.length);

            return result;
        } catch (Exception e) {
            throw new Errors.SerializationException("Failed to serialize message: " + e.getMessage(), null);
        }
    }

    /**
     * Deserialize binary data to message envelope
     */
    public static Types.MessageEnvelope deserialize(byte[] data) throws Errors.SerializationException {
        if (data.length < WIRE_HEADER_SIZE) {
            throw new Errors.SerializationException("Data too short for wire format", null);
        }

        ByteBuffer buffer = ByteBuffer.wrap(data);
        Types.MessageHeader header = deserializeHeader(buffer);
        byte[] bodyData = new byte[buffer.remaining()];
        buffer.get(bodyData);

        Types.MessageBody body = bodyData.length > 0 ? deserializeBody(bodyData) : null;

        Types.MessageEnvelope envelope = new Types.MessageEnvelope();
        envelope.setHeader(header);
        envelope.setBody(body);
        return envelope;
    }

    /**
     * Check if data is valid wire format
     */
    public static boolean isValid(byte[] data) {
        if (data.length < WIRE_HEADER_SIZE) return false;
        ByteBuffer buffer = ByteBuffer.wrap(data);
        int magic = buffer.getInt();
        return magic == WIRE_MAGIC;
    }

    // ============================================================
    // HEADER SERIALIZATION
    // ============================================================

    private static byte[] serializeHeader(Types.MessageHeader header) {
        ByteBuffer buffer = ByteBuffer.allocate(WIRE_HEADER_SIZE);

        buffer.putInt(WIRE_MAGIC);
        buffer.putInt(WIRE_VERSION);

        Integer typeCode = TYPE_MAP.get(header.getType());
        buffer.putInt(typeCode != null ? typeCode : 0);

        int flags = 0;
        if (header.getSignature() != null) flags |= 0x01;
        if (header.getNonce() != null) flags |= 0x02;
        if (header.getReceiver() != null) flags |= 0x04;
        if (header.getCorrelationId() != null) flags |= 0x08;
        if (header.getReplyTo() != null) flags |= 0x10;
        buffer.putInt(flags);

        return buffer.array();
    }

    private static Types.MessageHeader deserializeHeader(ByteBuffer buffer) {
        int magic = buffer.getInt();
        if (magic != WIRE_MAGIC) {
            throw new RuntimeException("Invalid magic number: " + String.format("%08x", magic));
        }

        int version = buffer.getInt();
        int typeCode = buffer.getInt();
        int flags = buffer.getInt();

        Types.MessageType type = TYPE_REVERSE_MAP.getOrDefault(typeCode, Types.MessageType.ERROR);

        Types.MessageHeader header = new Types.MessageHeader();
        header.setType(type);
        header.setVersion(String.format("%d.%d.%d",
                (version >> 24) & 0xFF,
                (version >> 16) & 0xFF,
                (version >> 8) & 0xFF));
        header.setMessageId(UUID.randomUUID().toString());
        header.setTimestamp(Instant.now());
        header.setSender("");
        header.setTtlSeconds(300);
        header.setPriority(0);
        header.setFlags(new ArrayList<>());

        if ((flags & 0x01) != 0) header.setSignature("placeholder");
        if ((flags & 0x02) != 0) header.setNonce("placeholder");
        if ((flags & 0x04) != 0) header.setReceiver("placeholder");
        if ((flags & 0x08) != 0) header.setCorrelationId("placeholder");
        if ((flags & 0x10) != 0) header.setReplyTo("placeholder");

        return header;
    }

    // ============================================================
    // BODY SERIALIZATION
    // ============================================================

    private static byte[] serializeBody(Types.MessageBody body) throws JsonProcessingException {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("content_type", body.getContentType());
        data.put("data", serializeValue(body.getData()));
        data.put("metadata", body.getMetadata() != null ? body.getMetadata() : new HashMap<>());
        if (body.getSchemaUri() != null) {
            data.put("schema_uri", body.getSchemaUri());
        }

        String json = objectMapper.writeValueAsString(data);
        return json.getBytes(StandardCharsets.UTF_8);
    }

    private static Types.MessageBody deserializeBody(byte[] data) throws Errors.SerializationException {
        try {
            Map<String, Object> parsed = objectMapper.readValue(data, Map.class);

            Types.MessageBody body = new Types.MessageBody();
            body.setContentType((String) parsed.getOrDefault("content_type", "application/json"));
            body.setMetadata((Map<String, Object>) parsed.getOrDefault("metadata", new HashMap<>()));
            body.setSchemaUri((String) parsed.get("schema_uri"));
            body.setSize(data.length);

            Object dataValue = parsed.get("data");
            body.setData(deserializeValue(dataValue));

            return body;
        } catch (Exception e) {
            throw new Errors.SerializationException("Failed to deserialize body: " + e.getMessage(), null);
        }
    }

    // ============================================================
    // VALUE SERIALIZATION
    // ============================================================

    @SuppressWarnings("unchecked")
    private static Object serializeValue(Types.VireoValue<?> value) {
        if (value == null) return null;

        switch (value.getType()) {
            case NULL:
                return null;
            case BOOLEAN:
            case INTEGER:
            case FLOAT:
            case STRING:
                return value.getValue();
            case BINARY:
                byte[] bytes = (byte[]) value.getValue();
                return Map.of("__type", "binary", "value", bytesToHex(bytes));
            case ARRAY:
                List<Types.VireoValue<?>> arr = (List<Types.VireoValue<?>>) value.getValue();
                List<Object> result = new ArrayList<>();
                for (Types.VireoValue<?> v : arr) {
                    result.add(serializeValue(v));
                }
                return result;
            case OBJECT:
                Map<String, Types.VireoValue<?>> obj = (Map<String, Types.VireoValue<?>>) value.getValue();
                Map<String, Object> objResult = new LinkedHashMap<>();
                for (Map.Entry<String, Types.VireoValue<?>> entry : obj.entrySet()) {
                    objResult.put(entry.getKey(), serializeValue(entry.getValue()));
                }
                return objResult;
            case TIMESTAMP:
                Instant ts = (Instant) value.getValue();
                return Map.of("__type", "timestamp", "value", ts.toString());
            case DID:
                return Map.of("__type", "did", "value", value.getValue());
            case SIGNATURE:
                byte[] sig = (byte[]) value.getValue();
                return Map.of("__type", "signature", "value", bytesToHex(sig));
            case NONCE:
                byte[] nonce = (byte[]) value.getValue();
                return Map.of("__type", "nonce", "value", bytesToHex(nonce));
            default:
                return value.getValue();
        }
    }

    @SuppressWarnings("unchecked")
    private static Types.VireoValue<?> deserializeValue(Object data) {
        if (data == null) {
            return new Types.VireoValue<>(Types.VireoType.NULL, null);
        }

        if (data instanceof Boolean) {
            return new Types.VireoValue<>(Types.VireoType.BOOLEAN, data);
        }

        if (data instanceof Integer) {
            return new Types.VireoValue<>(Types.VireoType.INTEGER, data);
        }

        if (data instanceof Double) {
            double d = (Double) data;
            if (d == (int) d) {
                return new Types.VireoValue<>(Types.VireoType.INTEGER, (int) d);
            }
            return new Types.VireoValue<>(Types.VireoType.FLOAT, data);
        }

        if (data instanceof String) {
            return new Types.VireoValue<>(Types.VireoType.STRING, data);
        }

        if (data instanceof List) {
            List<?> list = (List<?>) data;
            List<Types.VireoValue<?>> result = new ArrayList<>();
            for (Object item : list) {
                result.add(deserializeValue(item));
            }
            return new Types.VireoValue<>(Types.VireoType.ARRAY, result);
        }

        if (data instanceof Map) {
            Map<String, Object> map = (Map<String, Object>) data;

            // Check for special types
            if (map.containsKey("__type")) {
                String type = (String) map.get("__type");
                String value = (String) map.get("value");
                switch (type) {
                    case "binary":
                        return new Types.VireoValue<>(Types.VireoType.BINARY, hexToBytes(value));
                    case "timestamp":
                        return new Types.VireoValue<>(Types.VireoType.TIMESTAMP, Instant.parse(value));
                    case "did":
                        return new Types.VireoValue<>(Types.VireoType.DID, value);
                    case "signature":
                        return new Types.VireoValue<>(Types.VireoType.SIGNATURE, hexToBytes(value));
                    case "nonce":
                        return new Types.VireoValue<>(Types.VireoType.NONCE, hexToBytes(value));
                }
            }

            // Regular object
            Map<String, Types.VireoValue<?>> obj = new LinkedHashMap<>();
            for (Map.Entry<String, Object> entry : map.entrySet()) {
                obj.put(entry.getKey(), deserializeValue(entry.getValue()));
            }
            return new Types.VireoValue<>(Types.VireoType.OBJECT, obj);
        }

        return new Types.VireoValue<>(Types.VireoType.NULL, null);
    }

    // ============================================================
    // UTILITY FUNCTIONS
    // ============================================================

    private static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    private static byte[] hexToBytes(String hex) {
        if (hex == null || hex.isEmpty()) return new byte[0];
        int len = hex.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(hex.charAt(i), 16) << 4)
                    + Character.digit(hex.charAt(i + 1), 16));
        }
        return data;
    }
}