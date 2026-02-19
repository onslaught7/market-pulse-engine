### 2. Update `ROADMAP.md`

We are marking Sprint 1 as complete, upgrading the Sprint 2 plans to match reality, and updating your immediate checklist.

```markdown
# 🗺️ Project Roadmap: MarketPulse (The Wisdom & The Wire)

**Status:** `Sprint 1 Complete` | `Sprint 2 In Progress`
**Goal:** Build an Institutional-Grade Financial Intelligence Engine.
**Tech Stack:** Go (Gateway/Producer), Redis (Broker), Python (Worker/RAG), Qdrant (Vector Memory).

---

## 📐 System Architecture (The Pivot)

We are moving from a generic file uploader to a **Dual-Stream RAG System** using Microservices.

```mermaid
graph TD
    subgraph "The Wire (Real-Time)"
        GoProd[Go Feed Producer] -->|Polls| RSS[News Feeds]
        GoProd -->|POST JSON| GoService[Go Gateway]
        GoService -->|LPUSH "wire_queue"| Redis
    end

    subgraph "The Wisdom (Static)"
        PDFs[Financial Books / 10-Ks] -->|Manual Load| PySeed[Seed Script]
        PySeed -->|Direct Upsert| Qdrant
    end

    Redis -->|BRPOP| PyWorker[Python Worker]
    
    subgraph "The Brain (Processing)"
        PyWorker -->|Embedding| OpenAI
        PyWorker -->|Upsert w/ Metadata| Qdrant
    end

    User -->|Query| FastAPI[Query API (New)]
    FastAPI -->|Vector Search| Qdrant
    FastAPI -->|Synthesis| OpenAI

```

---

## 📅 Sprint 1: The "Wisdom" Foundation (Data Engineering) ✅

**Goal:** Seed the database with "Timeless Knowledge" (Books/PDFs).
**Status:** **COMPLETE**

* **1.1 Design Schema:** Built `config.py` and Qdrant collections with deterministic UUID indexing.
* **1.2 The Librarian Script:** Built `ingest_wisdom.py` to parse Graham, Dalio, and Lynch PDFs, chunk them cleanly, and attach "Metadata Passports" (Region/Topic).
* **1.3 Verification:** Ran semantic test queries to prove Qdrant successfully separates "Global" vs "Indian" financial contexts.

---

## 📅 Sprint 2: The "Wire" Pipeline (Real-Time Ingestion) 🏃 (Current)

**Goal:** Connect the system to the outside world to ingest live financial news.
**Architectural Upgrade:** Pivoted from a Python script to a dedicated Go Microservice for high-concurrency polling.

### Step 2.1: The Go Feed Producer (`producer/main.go`)

* **Tech:** Go + Goroutines.
* **Logic:**
1. Spawn Goroutines to fetch Yahoo Finance, WSJ, and CoinDesk concurrently.
2. Parse XML into unified JSON format.
3. Generate deterministic UUIDs from URLs to prevent duplicate indexing.
4. HTTP POST to the Gateway.



### Step 2.2: Upgrade the Worker (`worker.py`)

The worker is currently dumb. It needs a **Router**.

* **Logic Update:**
* Intercept tasks in the Redis queue.
* If `source_type == 'news'`, format the text, attach a timestamp, and upsert it into the database.



---

## 📅 Sprint 3: The "Consultant" API (The Brain)

**Goal:** Build the interface that allows us to *ask questions*.

### Step 3.1: The Query API (`api.py`)

* **Tech:** FastAPI (Python).
* **Endpoint:** `POST /ask`
* **Logic:**
1. **Dual-Search:** Query `wisdom` for Strategy, and query `wire` for Context (Recent News).
2. **Synthesis:** Send retrieved chunks to GPT-4o with a System Prompt: *"You are a Hedge Fund Analyst..."*



---

## 📅 Sprint 4: The "MarketPulse" Interface (The Demo)

**Goal:** A visual frontend for the video pitch.

### Step 4.1: Streamlit Dashboard (`app.py`)

* **Features:**
* **Sidebar:** "Live Wire" (Scrolling news feed from Qdrant).
* **Main Chat:** The "Consultant" interface.
* **Source Viewer:** When AI cites a book, show the page snippet.



---

## 🛠️ Immediate "Next Actions" Checklist

* [x] **Sprint 1:** Set up Qdrant and ingest "Wisdom" Books.
* [x] **Sprint 1:** Create `test_sprint1.py` to verify Metadata Filtering.
* [x] **Sprint 2:** Build the Go Producer (`producer/main.go`).
* [x] **Sprint 2:** Update `docker-compose.yml` with the Producer service.
* [ ] **Sprint 2:** Boot up Docker Compose and verify Producer -> Gateway -> Redis flow.
* [ ] **Sprint 2:** Update `worker.py` to process the live news and insert it into Qdrant.

```