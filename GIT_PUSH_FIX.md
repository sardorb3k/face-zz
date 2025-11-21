# Git Push Xatolikni Hal Qilish

## Muammo

```
fatal: could not read Username for 'https://github.com': No such device or address
```

Bu authentication muammosi. HTTPS orqali push qilishga harakat qilmoqda.

## Yechimlar

### 1. SSH orqali Push (Tavsiya)

Remote URL ni SSH ga o'zgartirish:

```bash
cd /home/sardor/apps/face-r
git remote set-url origin git@github.com:sardorb3k/face-r.git
git push
```

### 2. Personal Access Token (PAT)

Agar SSH yo'q bo'lsa, GitHub Personal Access Token ishlatish:

```bash
# 1. GitHub'da Personal Access Token yaratish:
# Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
# Generate new token (classic)
# Permissions: repo (full control)

# 2. Push qilish:
git push
# Username: sardorb3k
# Password: <your_personal_access_token>
```

### 3. Git Credential Helper

Credential'ni saqlash:

```bash
# Credential helper o'rnatish
git config --global credential.helper store

# Keyin push qilish (bir marta username/password kiritish kerak)
git push
```

### 4. SSH Key Yaratish (Agar yo'q bo'lsa)

```bash
# SSH key yaratish
ssh-keygen -t ed25519 -C "your_email@example.com"

# Public key ni ko'rsatish
cat ~/.ssh/id_ed25519.pub

# GitHub'ga qo'shish:
# Settings -> SSH and GPG keys -> New SSH key
```

## Tekshirish

```bash
# Remote URL ni tekshirish
git remote -v

# SSH connection test
ssh -T git@github.com
```

## Eng Oson Yechim

SSH orqali o'zgartirish:

```bash
git remote set-url origin git@github.com:sardorb3k/face-r.git
git push
```

