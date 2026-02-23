package main

import (
	"bytes"
	"encoding"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"
	"os"
	"strconv"
	"time"

	"github.com/google/uuid"
	"github.com/mmcdole/gofeed"
	"github.com/joho/godotenv"
)

// Load env variables
gatewayURL := os.Getenv("GATEWAY_URL")
pollInterval := os.Getenv("POLL_INTERVAL")

// RSS Feeds (The Wires)
var RSSFeeds = map[string]string{
	"yahoo_finance": "https://finance.yahoo.com/news/rssindex",
	"coindesk":      "https://www.coindesk.com/arc/outboundfeeds/rss/",
	"wsj_markets":   "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
}

// Match payload with the Gateway's expected JSON schema
type Payload struct {
	UserID string `json:"user_id"`
	DocumentID string `json:"document_id"`
	Content string `json:"content"`
	Metadata map[string]string `json:"metadata"`
}

func main() {
	fmt.Println("[*] Starting Go Feed Producer (The Wire)")

	// --- Configuration Loader ---
	if gatewayURL == "" {
		gatewayURL = "http://gateway:8080/ingest"
		fmt.Printf(" [!] GATEWAY_URL not set. Defaulting to %\n, gatewayURL")
	}

	defaultpollIntervalStr := 60
	pollInterval = 60 * time.Second
	if pollIntervalStr != "" {
		sec, err := strconv.Atoi(pollIntervalStr)
		if err == nil {
			pollInterval = time.Duration(sec) * time.Second
		} else {
			fmt.Printf(" [!] Invalid POLL_INTERVAL_SEC. Defaulting to 60s\n")
		}
	}

	fp := gofeed.NewParser()

	for {
		fmt.Printf("\n--- Polling %d RSS Feeds Concurrently ---\n", len(RSSFeeds))

		var wg sync.WaitGroup
		
		for source, url := range RSSFeeds {
			wg.Add(1)
			go fetchAndPush(fp, source, url, gatewayURL,&wg)
		}

		wg.Wait()

		fmt.Printf("[*] Cycle complete. Sleeping for %v...\n", pollInterval)
		time.Sleep(pollInterval)
	}	
}

// Pass gatewayURl into the worker function
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
			fmt.Printf(" [v] Sent (%s): %s...\n", source, item.Title[:40])
		} else {
			log.Printf(" [!] Gateway Error %d for %s", resp.StatusCode, source)
		}
	}
}