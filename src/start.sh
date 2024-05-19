#!/bin/bash

gunicorn -w 1 --threads 100 app:app