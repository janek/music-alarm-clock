#!/bin/bash
curl \
    -X "PUT" "https://api.spotify.com/v1/me/player/play" \
    --data "{\"context_uri\":\"spotify:album:5ht7ItJgpBH7W6vJ5BqpPr\",\"offset\":{\"position\":5},\"position_ms\":0}" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer BQDql0YcRUKWEwqsMbZgpr6dQe1Ps8sbUn9o7P0SIh2THE4ZQ0RMdNeYJhkEkJZ0X3krHbqIY4t3028w5HzTjzfFTiuguIzQdU_9mItfl0rdtbJ1FqtxqosFBEKqmxhxRObAiunWhp9r438Tr_L2OnOK3f2d222loskwQn6ITy-hRGs6kyUqc5fDhkzA7pCqQ_JgdaKPJmm-FQioYoqFEDCqxXCXI1jne0839HYjqP069KAIJfq8jzS9rwKilyoMkDbJMg8zsLg99tawGd2nIA"
