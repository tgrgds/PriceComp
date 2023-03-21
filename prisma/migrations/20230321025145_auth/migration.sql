-- CreateTable
CREATE TABLE "User" (
    "hash" TEXT NOT NULL PRIMARY KEY,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateIndex
CREATE UNIQUE INDEX "User_hash_key" ON "User"("hash");
