# Build Stage
FROM golang:1.21-alpine AS builder
WORKDIR /app
# Initialize the module
RUN go mod init gateway
RUN go get github.com/gofiber/fiber/v2
RUN go get github.com/redis/go-redis/v9
COPY . .
RUN go build -o main .

# Run Stage
FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/main .
CMD ["./main"]