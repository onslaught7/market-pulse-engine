package main

import (
	"encoding/json"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/redis/go-redis/v9"

	"go.opentelemetry.io/otel"
)

// Define the Data Contract we expect from the user
type IngestRequest struct {
	UserID     string            `json:"user_id"`
	DocumentID string            `json:"document_id"`
	Content    string            `json:"content"`
	Metadata   map[string]string `json:"metadata"`
}

// var ctx = context.Background()

func main() {
	tp, err := initTracer("vortex-gateway")
	if err != nil {
		log.Fatalf("Failed to initialize tracer: %v", err)
	}

	defer func() {
		if err := tp.Shutdown(ctx); err != nil {
			log.Printf("Error shutting down tracer provider: %v", err)
		}
	}()

	tracer := otel.Tracer("gateway")

	redisAddr := os.Getenv("REDIS_ADDR")
	if redisAddr == "" {
		redisAddr = "localhost:6379" // Default for local testing
	}

	rdb := redis.NewClient(&redis.Options{
		Addr: redisAddr,
	})

	// Test connection
	if _, err := rdb.Ping(ctx).Result(); err != nil {
		log.Fatalf("Could not connect to Redis: %v", err)
	}

	app := fiber.New()

	app.Post("/ingest", func(c *fiber.Ctx) error {
		// This attaches the trace to the actual request lifecycle.
		ctx, span := tracer.Start(c.UserContext(), "gateway.ingest")
		defer span.End()

		// Parse JSON
		payload := new(IngestRequest)
		if err := c.BodyParser(payload); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Invalid JSON"})
		}

		// Validate required fields
		if payload.UserID == "" || payload.DocumentID == "" || payload.Content == "" {
			return c.Status(400).JSON(fiber.Map{"error": "Missing required fields"})
		}

		// Re-marshal clean payload (only contract fields reach Redis)
		cleanJSON, err := json.Marshal(payload)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": "Failed to process payload"})
		}

		// Push to Redis
		ctxRedis, redisSpan := tracer.Start(ctx, "redis.enqueue")
		defer redisSpan.End()

		err = rdb.LPush(ctxRedis, "ingestion_queue", cleanJSON).Err()
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": "Redis Queue Failed"})
		}

		// Response Instantly
		return c.Status(202).JSON(fiber.Map{
			"status":  "accepted",
			"message": "Document Queued for Processing",
			"data":    payload.DocumentID,
		})
	})

	log.Fatal(app.Listen(":8080"))
}