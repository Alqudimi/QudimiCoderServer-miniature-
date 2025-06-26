from transformers import AutoModelForCausalLM, BitsAndBytesConfig

nf4_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
)

model = AutoModelForCausalLM.from_pretrained(
    "bigcode/starcoderbase-350m",
    quantization_config=nf4_config
)

model.save_pretrained("./local_model")
