-- CreateTable
CREATE TABLE "Product" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "sku" TEXT NOT NULL,
    "store_id" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "price" REAL NOT NULL,
    "in_stock" BOOLEAN NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "Product_id_key" ON "Product"("id");
