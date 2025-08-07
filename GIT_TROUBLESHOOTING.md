# Git Push Troubleshooting Guide

## 🚨 **"Failed Refs" Error Resolution**

### **Common Causes & Solutions**

---

## 🔍 **Step 1: Diagnose the Issue**

### **Check Git Status**

```bash
# Check current status
git status

# Check remote configuration
git remote -v

# Check branch information
git branch -a
```

### **Check for Specific Error Messages**

```bash
# Try push with verbose output
git push -v origin main

# Check for detailed error information
git push --verbose origin main
```

---

## 🛠️ **Step 2: Common Solutions**

### **Solution 1: Force Push (Use with Caution)**

```bash
# If you're sure your local changes are correct
git push --force-with-lease origin main

# Or force push (dangerous - overwrites remote)
git push --force origin main
```

### **Solution 2: Pull and Merge**

```bash
# Pull latest changes first
git pull origin main

# Resolve any conflicts, then push
git push origin main
```

### **Solution 3: Reset and Reapply**

```bash
# Reset to match remote
git fetch origin
git reset --hard origin/main

# Reapply your changes
git add .
git commit -m "Your commit message"
git push origin main
```

---

## 🔧 **Step 3: Advanced Troubleshooting**

### **Check Remote Repository**

```bash
# Verify remote URL
git remote get-url origin

# Test connection to remote
ssh -T git@github.com  # For SSH
# or
git ls-remote origin   # For HTTPS
```

### **Fix Authentication Issues**

```bash
# For HTTPS - set credentials
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# For SSH - check key
ssh-add -l
```

### **Clean and Reset**

```bash
# Clean untracked files
git clean -fd

# Reset to last known good state
git reset --hard HEAD~1

# Or reset to specific commit
git reset --hard <commit-hash>
```

---

## 📋 **Step 4: Specific Error Scenarios**

### **Scenario 1: "Rejected" Error**

```bash
# Remote has changes you don't have locally
git fetch origin
git merge origin/main
git push origin main
```

### **Scenario 2: "Permission Denied"**

```bash
# Check SSH key
ssh -T git@github.com

# Or use HTTPS with token
git remote set-url origin https://github.com/username/repo.git
```

### **Scenario 3: "Non-fast-forward"**

```bash
# Pull changes first
git pull origin main

# Or rebase your changes
git pull --rebase origin main
git push origin main
```

### **Scenario 4: "Refusing to merge unrelated histories"**

```bash
# Allow unrelated histories
git pull origin main --allow-unrelated-histories
git push origin main
```

---

## 🚀 **Step 5: Emergency Recovery**

### **Complete Reset (Nuclear Option)**

```bash
# Backup your current work
cp -r . ../backup_$(date +%Y%m%d_%H%M%S)

# Reset everything
git fetch origin
git reset --hard origin/main
git clean -fd

# Reapply your changes manually
# Copy files from backup to current directory
git add .
git commit -m "Reapplied changes after reset"
git push origin main
```

### **Create New Branch**

```bash
# Create new branch from current state
git checkout -b backup-branch

# Reset main to remote
git checkout main
git reset --hard origin/main

# Cherry-pick your changes
git cherry-pick backup-branch
git push origin main
```

---

## 🔍 **Step 6: Prevention**

### **Best Practices**

```bash
# Always pull before making changes
git pull origin main

# Use meaningful commit messages
git commit -m "Descriptive commit message"

# Check status frequently
git status

# Use branches for features
git checkout -b feature-branch
git push origin feature-branch
```

### **Git Configuration**

```bash
# Set up proper user info
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch
git config --global init.defaultBranch main

# Set push strategy
git config --global push.default simple
```

---

## 📊 **Step 7: Debugging Commands**

### **Check Repository State**

```bash
# View commit history
git log --oneline -10

# Check remote branches
git branch -r

# Check local branches
git branch

# Check for uncommitted changes
git diff
git diff --cached
```

### **Check Remote Configuration**

```bash
# List all remotes
git remote -v

# Check remote branches
git ls-remote origin

# Test remote connection
git fetch origin
```

---

## 🎯 **Quick Fix Commands**

### **For Most Common Issues**

```bash
# 1. Pull latest changes
git pull origin main

# 2. Add your changes
git add .

# 3. Commit
git commit -m "Your commit message"

# 4. Push
git push origin main
```

### **If That Doesn't Work**

```bash
# 1. Fetch latest
git fetch origin

# 2. Reset to remote
git reset --hard origin/main

# 3. Reapply changes
git add .
git commit -m "Reapplied changes"
git push origin main
```

---

## ⚠️ **Warning Signs**

### **When to Be Careful**

- ❌ **Don't force push** if others are working on the same repository
- ❌ **Don't delete remote branches** without coordination
- ❌ **Don't commit sensitive data** (API keys, passwords)
- ❌ **Don't ignore merge conflicts** - resolve them properly

### **Safe Practices**

- ✅ **Always pull before pushing**
- ✅ **Use descriptive commit messages**
- ✅ **Test your code before pushing**
- ✅ **Use branches for features**
- ✅ **Backup important work**

---

## 📞 **Getting Help**

### **If Nothing Works**

1. **Check GitHub Status**: https://www.githubstatus.com/
2. **Verify Repository Permissions**: Check if you have push access
3. **Contact Repository Admin**: If it's a shared repository
4. **Create New Repository**: As last resort

### **Useful Commands for Debugging**

```bash
# Check git version
git --version

# Check git configuration
git config --list

# Check repository size
du -sh .git

# Check for large files
find . -size +100M
```

---

## 🔄 **Alternative Solutions**

### **If Git Push Still Fails**

```bash
# Try different remote URL
git remote set-url origin https://github.com/username/repo.git

# Or use SSH
git remote set-url origin git@github.com:username/repo.git

# Try pushing to different branch
git push origin main:backup-branch
```

### **Last Resort**

```bash
# Clone fresh repository
git clone https://github.com/username/repo.git fresh-repo
cd fresh-repo

# Copy your changes
cp -r ../original-repo/* .

# Add and commit
git add .
git commit -m "Fresh start with changes"
git push origin main
```

---

_This guide covers the most common git push issues. If you're still having problems, please share the specific error message for more targeted help._
