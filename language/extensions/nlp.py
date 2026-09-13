# ============================================================
# VIREO NLP EXTENSIONS
# Natural Language Processing operations
# ============================================================

NLP_GRAMMAR = """
// ============================================================
// NLP EXTENSIONS GRAMMAR
// ============================================================

nlp_op: "text" "." operation "(" [params] ")"

operation: "tokenize" | "stem" | "lemmatize" | "clean"
         | "embed" | "classify" | "ner" | "sentiment"
         | "translate" | "summarize" | "generate"
         | "extract_entities" | "extract_keywords"
         | "question_answering" | "text_completion"
         | "grammar_check" | "spell_check" | "paraphrase"
         | "topic_modeling" | "text_clustering"

params: param ["," param]*
param: IDENTIFIER "=" value

value: NUMBER
     | STRING
     | "true" | "false"
     | array

nlp_model: "nlp_model" IDENTIFIER block

nlp_model_type: "BERT" | "GPT" | "T5" | "RoBERTa"
              | "DistilBERT" | "ALBERT" | "XLNet"
              | "ELECTRA" | "BART" | "Longformer"

nlp_task: "task" IDENTIFIER
"""


class NLPParser:
    """Parser for NLP extensions."""
    
    def __init__(self):
        self.grammar = NLP_GRAMMAR
    
    def parse_text_op(self, op: str, params: dict) -> dict:
        return {"type": "nlp", "op": op, "params": params}
    
    def parse_tokenize(self, text: str) -> dict:
        return {"type": "tokenize", "text": text}
    
    def parse_embed(self, text: str, model: str = "default") -> dict:
        return {"type": "embed", "text": text, "model": model}
    
    def parse_classify(self, text: str, model: str = "default") -> dict:
        return {"type": "classify", "text": text, "model": model}
    
    def parse_sentiment(self, text: str) -> dict:
        return {"type": "sentiment", "text": text}
    
    def parse_translate(self, text: str, target_lang: str) -> dict:
        return {"type": "translate", "text": text, "target": target_lang}
    
    def parse_summarize(self, text: str, max_length: int = 100) -> dict:
        return {"type": "summarize", "text": text, "max_length": max_length}


nlp_grammar = NLP_GRAMMAR