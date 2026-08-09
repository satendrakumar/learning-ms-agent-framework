 export VLLM_LOGGING_LEVEL=DEBUG
 vllm serve Qwen/Qwen3.5-4B  --max-model-len=8192 --default-chat-template-kwargs '{"enable_thinking": false}'  --enable-prefix-caching  --enable-auto-tool-choice  --tool-call-parser qwen3_coder --trust-remote-code --enable-log-requests --enable-log-outputs



 docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HF_TOKEN=$HF_TOKEN" \
    -e VLLM_LOGGING_LEVEL=DEBUG \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model Qwen/Qwen3.5-4B  --max-model-len=8192 --default-chat-template-kwargs '{"enable_thinking": false}'  --enable-prefix-caching  --enable-auto-tool-choice  --tool-call-parser qwen3_coder --trust-remote-code --enable-log-requests --enable-log-outputs