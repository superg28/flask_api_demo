# flask_api_demo
Demo code of a flask api running in docker with a mongodb as a database

## get a JWT auth token
```bash
TOKEN=$(curl -s -X POST -H 'Content-Type: multipart/form-data' -F 'username=superone' -F 'password=superone' http://YOUR_DOMAIN_HERE/auth/login | jq -r '.token')
```

## endpoints to browse

```bash
curl -H 'Accept: application/json' -H "Authorization: Bearer ${TOKEN}" http://YOUR_DOMAIN_HERE/api/profiles/ | jq .
```
- /api/profiles/
- /api/profiles/PROFILE_NAME
- /api/profiles/cards
- /api/cards
- /api/cards/CARD_ID