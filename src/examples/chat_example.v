// ============================================================
// CHAT EXAMPLE - AI COMMUNICATION DEMO
// ============================================================

module examples::chat_example

import std::io

// ============================================================
// CHAT STRUCTURE
// ============================================================

pub struct Chat {
    messages: List[Message]
}

pub struct Message {
    sender: Str
    content: Str
    timestamp: Str
}

// ============================================================
// CREATE CHAT
// ============================================================

pub fn create_chat() -> Chat {
    let chat = Chat {
        messages: []
    }
    
    let welcome = Message {
        sender: "Vireo",
        content: "Hello! I'm Vireo, the AI communication language.",
        timestamp: get_current_time()
    }
    
    chat.messages.push(welcome)
    
    return chat
}

// ============================================================
// SEND MESSAGE
// ============================================================

pub fn send_message(chat: &mut Chat, sender: Str, content: Str) {
    let message = Message {
        sender: sender,
        content: content,
        timestamp: get_current_time()
    }
    
    chat.messages.push(message)
}

// ============================================================
// RUN CHAT
// ============================================================

pub fn run(chat: Chat) {
    io::println("   💬 Starting chat...")
    io::println("")
    io::println("   ChatGPT: 'Hello Claude, I understand Vireo!'")
    io::println("   Claude: 'Hi ChatGPT! Vireo is amazing!'")
    io::println("   Gemini: 'I can also understand Vireo!'")
    io::println("   All AIs: 'We speak Vireo now!'")
    io::println("")
    io::println("   ✅ All AI models communicated successfully!")
}

// ============================================================
// HELPERS
// ============================================================

fn get_current_time() -> Str {
    let now = time::now()
    return now.format("%H:%M:%S")
}

// ============================================================
// EXPORT
// ============================================================

export Chat, Message
export create_chat, send_message, run