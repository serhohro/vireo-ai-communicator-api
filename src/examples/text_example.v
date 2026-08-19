// ============================================================
// TEXT EXAMPLE - NLP ON VIREO
// ============================================================

module examples::text_example

import std::io

// ============================================================
// TEXT PROCESSING
// ============================================================

pub struct TextProcessor {
    vocab: Dict[Str, Int]
    max_length: Int
}

pub fn create_text_processor(vocab_size: Int, max_length: Int) -> TextProcessor {
    let mut vocab = Dict::new()
    
    vocab["<PAD>"] = 0
    vocab["<UNK>"] = 1
    vocab["<START>"] = 2
    vocab["<END>"] = 3
    
    for i in 4..vocab_size {
        vocab[format("word_{}", i)] = i
    }
    
    return TextProcessor {
        vocab: vocab,
        max_length: max_length
    }
}

pub fn tokenize(processor: TextProcessor, text: Str) -> List[Int] {
    let mut tokens = []
    let words = text.split()
    
    for word in words {
        if processor.vocab.contains(word) {
            tokens.push(processor.vocab[word])
        } else {
            tokens.push(processor.vocab["<UNK>"])
        }
    }
    
    if tokens.len() > processor.max_length {
        tokens = tokens[0:processor.max_length]
    } else {
        while tokens.len() < processor.max_length {
            tokens.push(processor.vocab["<PAD>"])
        }
    }
    
    return tokens
}

// ============================================================
// SENTIMENT ANALYSIS
// ============================================================

@neural
fn sentiment_model(text_embedding: Tensor<F32, [batch, 300]>) -> Tensor<F32, [batch, 2]> {
    let x = dense(text_embedding, 128, ReLU)
    let x = dropout(x, 0.3)
    let x = dense(x, 64, ReLU)
    let x = dropout(x, 0.3)
    return dense(x, 2, Softmax)
}

pub fn analyze_sentiment(text: Str) -> Str {
    io::println("   📝 Analyzing text...")
    
    let embedding = Tensor<F32, [1, 300]>::random()
    let result = sentiment_model(embedding)
    
    let positive_prob = result[0, 0]
    let negative_prob = result[0, 1]
    
    if positive_prob > negative_prob {
        return "Positive 😊"
    } else {
        return "Negative 😞"
    }
}

// ============================================================
// DEMO
// ============================================================

pub fn demo_text_processing() {
    io::println("   📝 Text processing demo...")
    io::println("")
    
    let processor = create_text_processor(1000, 50)
    
    let texts = [
        "This is a great day!",
        "I love Vireo!",
        "This is terrible.",
        "Vireo is the future."
    ]
    
    for text in texts {
        let tokens = tokenize(processor, text)
        let sentiment = analyze_sentiment(text)
        io::println(f"   Text: '{text}'")
        io::println(f"   Tokens: {tokens}")
        io::println(f"   Sentiment: {sentiment}")
        io::println("")
    }
}

// ============================================================
// EXPORT
// ============================================================

export TextProcessor, create_text_processor, tokenize
export sentiment_model, analyze_sentiment
export demo_text_processing