# Build Stage
FROM --platform=$BUILDPLATFORM golang:1.25-alpine AS builder

WORKDIR /src

# Install git for go module downloads
RUN apk add --no-cache git

# Cache dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy source
COPY . .

# Build static binary
ENV CGO_ENABLED=0

RUN go build \
    -ldflags="-s -w" \
    -trimpath \
    -o /app/main


# Runtime Stage
FROM gcr.io/distroless/base-debian12

WORKDIR /app

# Copy compiled binary only
COPY --from=builder /app/main .

# Drop root privileges
USER nonroot:nonroot

# Expose port
EXPOSE 8080

# Run application
ENTRYPOINT [ "./main" ]