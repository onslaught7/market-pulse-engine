package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/joho/godotenv"
	"github.com/mmcdole/gofeed"
)

// Package-level vars (loaded in main after godotenv)
var (
	gatewayURL   string
	pollInterval time.Duration
)

// RSS Feeds (The Wires)
var RSSFeeds = map[string]string{
	"yahoo_finance": "https://finance.yahoo.com/news/rssindex",
	"coindesk":      "https://www.coindesk.com/arc/outboundfeeds/rss/",
	"wsj_markets":   "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
}

// Match payload with the Gateway's expected JSON schema
type Payload struct {
	UserID     string            `json:"user_id"`
	DocumentID string            `json:"document_id"`
	Content    string            `json:"content"`
	Metadata   map[string]string `json:"metadata"`
}

func main() {
	fmt.Println("[*] Starting Go Feed Producer (The Wire)")

	// Load .env file (optional — won't error if missing in Docker)
	_ = godotenv.Load()

	// --- Configuration Loader ---
	gatewayURL = os.Getenv("GATEWAY_URL")
	if gatewayURL == "" {
		gatewayURL = "http://gateway:8080/ingest"
		fmt.Printf(" [!] GATEWAY_URL not set. Defaulting to %s\n", gatewayURL)
	}

	pollInterval = 60 * time.Second
	if pollIntervalStr := os.Getenv("POLL_INTERVAL"); pollIntervalStr != "" {
		sec, err := strconv.Atoi(pollIntervalStr)
		if err == nil {
			pollInterval = time.Duration(sec) * time.Second
		} else {
			fmt.Printf(" [!] Invalid POLL_INTERVAL. Defaulting to 60s\n")
		}
	}

	fp := gofeed.NewParser()

	for {
		fmt.Printf("\n--- Polling %d RSS Feeds Concurrently ---\n", len(RSSFeeds))

		var wg sync.WaitGroup

		for source, url := range RSSFeeds {
			wg.Add(1)
			go fetchAndPush(fp, source, url, gatewayURL, &wg)
		}

		wg.Wait()

		fmt.Printf("[*] Cycle complete. Sleeping for %v...\n", pollInterval)
		time.Sleep(pollInterval)
	}
}

// Pass gatewayURL into the worker function
func fetchAndPush(fp *gofeed.Parser, source string, url string, gatewayURL string, wg *sync.WaitGroup) {
	defer wg.Done()

	feed, err := fp.ParseURL(url)
	if err != nil {
		log.Printf("[!] Error parsing %s: %v", source, err)
		return
	}

	limit := 3
	if len(feed.Items) < limit {
		limit = len(feed.Items)
	}

	for _, item := range feed.Items[:limit] {
		docID := uuid.NewSHA1(uuid.NameSpaceURL, []byte(item.Link)).String()
		content := fmt.Sprintf("%s\n\n%s", item.Title, item.Description)

		payload := Payload{
			UserID:     "system_feed_poller",
			DocumentID: docID,
			Content:    content,
			Metadata: map[string]string{
				"source":    source,
				"url":       item.Link,
				"published": item.Published,
				"type":      "news",
				"region":    "global",
			},
		}

		jsonData, err := json.Marshal(payload)
		if err != nil {
			continue
		}

		resp, err := http.Post(gatewayURL, "application/json", bytes.NewBuffer(jsonData))
		if err != nil {
			log.Printf("[!] Connection refused by Gateway for %s", source)
			continue
		}
		defer resp.Body.Close()

		if resp.StatusCode == 202 {
			title := item.Title
			if len(title) > 40 {
				title = title[:40]
			}
			fmt.Printf(" [v] Sent (%s): %s...\n", source, title)
		} else {
			log.Printf(" [!] Gateway Error %d for %s", resp.StatusCode, source)
		}
	}
}
