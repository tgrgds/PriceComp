-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_Product" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "sku" TEXT NOT NULL,
    "sku_trunc" TEXT NOT NULL DEFAULT '',
    "store_id" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "price" REAL NOT NULL,
    "in_stock" BOOLEAN NOT NULL,
    "created" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated" DATETIME NOT NULL
);
INSERT INTO "new_Product" ("created", "id", "in_stock", "price", "sku", "store_id", "updated", "url") SELECT "created", "id", "in_stock", "price", "sku", "store_id", "updated", "url" FROM "Product";
DROP TABLE "Product";
ALTER TABLE "new_Product" RENAME TO "Product";
CREATE UNIQUE INDEX "Product_id_key" ON "Product"("id");
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
