# Stage 1
FROM --platform=$BUILDPLATFORM golang:1.25-alpine AS builder

WORKDIR /src
RUN apk add --no-cache git

COPY go.mod go.sum ./
RUN go mod download

COPY . .

ENV CGO_ENABLED=0

RUN go build \
    -ldflags="-s -w" \
    -trimpath \
    -o /app/main

# Stage 2
FROM gcr.io/distroless/base-debian12

WORKDIR /app

COPY --from=builder /app/main .

USER nonroot:nonroot

CMD ["./main"]