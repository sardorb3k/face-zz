# Git Push Yechimlari

## Muammo

Git push authentication muammosi.

## Yechim 1: GitHub Host Key Qo'shish (Bajarildi)

```bash
ssh-keyscan github.com >> ~/.ssh/known_hosts
```

## Yechim 2: SSH Key Tekshirish

Agar SSH key yo'q bo'lsa:

```bash
# SSH key yaratish
ssh-keygen -t ed25519 -C "your_email@example.com"

# Public key ni ko'rsatish
cat ~/.ssh/id_ed25519.pub

# GitHub'ga qo'shish:
# https://github.com/settings/keys
# New SSH key -> Key ni qo'shish
```

## Yechim 3: HTTPS orqali Personal Access Token

Agar SSH ishlamasa:

```bash
# Remote URL ni HTTPS ga qaytarish
git remote set-url origin https://github.com/sardorb3k/face-r.git

# GitHub'da Personal Access Token yaratish:
# https://github.com/settings/tokens
# Generate new token (classic)
# Permissions: repo (full control)

# Push qilish
git push
# Username: sardorb3k
# Password: <your_personal_access_token>
```

## Yechim 4: Git Credential Helper

```bash
# Credential helper o'rnatish
git config --global credential.helper store

# Push qilish (bir marta username/password kiritish)
git push
```

## Tekshirish

```bash
# Remote URL
git remote -v

# SSH test
ssh -T git@github.com

# Status
git status
```

## Eng Oson Yechim

Agar SSH key mavjud bo'lsa:
```bash
git push
```

Agar SSH key yo'q bo'lsa, HTTPS orqali:
```bash
git remote set-url origin https://github.com/sardorb3k/face-r.git
git push
# Username: sardorb3k
# Password: <personal_access_token>
```

