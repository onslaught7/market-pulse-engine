# Build Stage
FROM golang:1.25-alpine AS builder
WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o main .

# Run Stage
FROM alpine:3.21
RUN adduser -D appuser
WORKDIR /home/appuser

# Install root certificates so GO can make HTTPS requests to Yahoo/CoinDesk
RUN apk add --no-cache ca-certificates
COPY --from=builder /app/main .
USER appuser
CMD ["./main"]