export set https_proxy=localhost:8080
export set http_proxy=localhost:8080
google-chrome --headless --disable-gpu --dump-dom --aggressive-cache-discard https://www.amazon.com
