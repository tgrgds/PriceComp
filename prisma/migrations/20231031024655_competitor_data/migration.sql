-- CreateTable
CREATE TABLE "Competitor" (
    "store_id" TEXT NOT NULL PRIMARY KEY,
    "last_scrape" DATETIME,
    "last_scrape_duration" REAL,
    "last_scrape_failed" BOOLEAN DEFAULT false
);

-- CreateIndex
CREATE UNIQUE INDEX "Competitor_store_id_key" ON "Competitor"("store_id");
