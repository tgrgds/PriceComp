#!/bin/bash

prisma migrate deploy

uvicorn main:app --host 0.0.0.0 --port 80 --proxy-headers
