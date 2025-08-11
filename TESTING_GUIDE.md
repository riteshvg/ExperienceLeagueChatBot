# 🧪 **TESTING GUIDE FOR ADOBE ANALYTICS CHATBOT**

## 📋 **Overview**

This guide will walk you through testing the Adobe Analytics ChatBot application step by step. The application consists of three main components that work together to create segments in Adobe Analytics.

---

## 🚀 **Quick Start Testing**

### **1. Run the Manual Test Script**
```bash
# Activate virtual environment
source venv/bin/activate

# Run the comprehensive test
python test_app_manually.py
```

**Expected Result:** All 5 tests should pass ✅

---

## 📱 **Step-by-Step Manual Testing**

### **Prerequisites**
- Ensure all Streamlit apps are running
- Have Adobe Analytics credentials configured
- Virtual environment activated

### **Step 1: Test Main Chatbot (Port 8503)**

**URL:** http://localhost:8503

**What to Test:**
1. **General Questions:**
   - Ask: "What is Adobe Analytics?"
   - Expected: Normal chatbot response

2. **Segment Creation Requests:**
   - Ask: "Create a segment for mobile users from California"
   - Expected: 
     - Intent detection: "segment"
     - Segment creation workflow displayed
     - "Start Segment Builder" button appears

3. **Other Actions:**
   - Ask: "How do I create a report?"
   - Expected: Action detection for "report"

**Success Indicators:**
- ✅ Intent detection working
- ✅ Segment workflow triggered
- ✅ UI elements displayed correctly

### **Step 2: Test Segment Builder (Port 8502)**

**URL:** http://localhost:8502

**What to Test:**
1. **Direct Access:**
   - Navigate directly to the segment builder
   - Should show intent detection step

2. **From Main App:**
   - Click "Start Segment Builder" from main app
   - Should pre-populate with detected intent
   - Skip to configuration step

3. **Manual Configuration:**
   - Fill in segment details:
     - Name: "Test Mobile Users"
     - Description: "Test segment for mobile users"
     - RSID: "argupaepdemo"
     - Target Audience: "visitors"
     - Rules: Add device type rule

4. **Validation:**
   - Test with invalid data
   - Verify error messages appear
   - Confirm validation prevents submission

**Success Indicators:**
- ✅ Multi-step workflow working
- ✅ Configuration validation working
- ✅ Payload generation successful

### **Step 3: Test Adobe API Integration (Port 8501)**

**URL:** http://localhost:8501

**What to Test:**
1. **API Connection:**
   - Test API connection
   - Verify company ID retrieval
   - Check access token generation

2. **Segment Creation:**
   - Create sample segments
   - Verify successful creation
   - Check segment IDs returned

3. **Error Handling:**
   - Test with invalid credentials
   - Verify error messages
   - Check retry mechanisms

**Success Indicators:**
- ✅ API connection successful
- ✅ Authentication working
- ✅ Segment creation successful

---

## 🔧 **Advanced Testing Scenarios**

### **Scenario 1: Complete End-to-End Workflow**

1. **Start in Main App:**
   - Ask: "Create a segment for desktop users with high page views from New York"

2. **Follow the Workflow:**
   - Verify intent detection
   - Check segment suggestions
   - Click "Start Segment Builder"

3. **Complete Segment Creation:**
   - Fill in configuration
   - Validate settings
   - Create segment

4. **Verify in Adobe Analytics:**
   - Check if segment appears in Adobe Analytics
   - Verify segment ID and details

**Expected Result:** Complete workflow from query to segment creation

### **Scenario 2: Error Handling and Recovery**

1. **Test Validation Errors:**
   - Try to create segment with empty name
   - Test invalid RSID format
   - Submit without required fields

2. **Test API Errors:**
   - Use invalid credentials
   - Test network timeouts
   - Verify error recovery

3. **Test User Recovery:**
   - Check error messages are clear
   - Verify recovery suggestions
   - Test retry mechanisms

**Expected Result:** Graceful error handling with user-friendly messages

### **Scenario 3: Complex Segment Definitions**

1. **Test Multiple Rules:**
   - Create segments with device + geographic + behavioral rules
   - Verify rule combinations work correctly

2. **Test Different Rule Types:**
   - String comparisons (streq, contains)
   - Numeric comparisons (gt, lt, gte, lte)
   - Verify correct Adobe Analytics syntax

3. **Test Edge Cases:**
   - Very long segment names
   - Special characters in descriptions
   - Complex rule structures

**Expected Result:** Robust handling of complex configurations

---

## 🧪 **Automated Testing**

### **Run All Tests**
```bash
# Comprehensive validation test
python validate_segment_execution.py

# Simple segment test
python test_simple_segment.py

# Manual component testing
python test_app_manually.py

# Integration workflow test
python test_integration_workflow.py
```

### **Test Specific Components**
```bash
# Test Adobe API only
python -c "from adobe_api import get_company_id; print(get_company_id())"

# Test intent detection only
python -c "from app import detect_create_action; print(detect_create_action('Create a segment'))"

# Test segment builder only
python -c "from segment_builder import SegmentBuilder; print('Builder imported successfully')"
```

---

## 📊 **Testing Checklist**

### **Core Functionality**
- [ ] **Intent Detection**
  - [ ] Segment creation requests detected
  - [ ] Other actions detected correctly
  - [ ] No false positives

- [ ] **Segment Suggestions**
  - [ ] Names generated appropriately
  - [ ] Descriptions are clear
  - [ ] Rules are valid Adobe Analytics syntax

- [ ] **Configuration Building**
  - [ ] Payload structure correct
  - [ ] Validation working
  - [ ] Error handling functional

### **Integration**
- [ ] **Main App → Segment Builder**
  - [ ] Data passed correctly
  - [ ] Pre-population working
  - [ ] Navigation smooth

- [ ] **Segment Builder → Adobe API**
  - [ ] Payload format correct
  - [ ] API calls successful
  - [ ] Response handling working

### **User Experience**
- [ ] **Workflow**
  - [ ] Steps are clear
  - [ ] Progress indication
  - [ ] Error recovery

- [ ] **Validation**
  - [ ] Real-time feedback
  - [ ] Clear error messages
  - [ ] Helpful suggestions

---

## 🚨 **Common Issues and Solutions**

### **Issue: "Port already in use"**
**Solution:**
```bash
# Find processes using the port
lsof -i :8501
lsof -i :8502
lsof -i :8503

# Kill the process
kill -9 <PID>
```

### **Issue: "Adobe API connection failed"**
**Solution:**
1. Check credentials in Streamlit secrets
2. Verify Adobe Analytics access
3. Check network connectivity

### **Issue: "Segment creation failed"**
**Solution:**
1. Verify RSID is correct
2. Check segment name uniqueness
3. Validate rule syntax

### **Issue: "Import errors"**
**Solution:**
1. Activate virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Check Python path

---

## 🎯 **Success Criteria**

### **Minimum Viable Testing**
- [ ] All 5 manual tests pass
- [ ] End-to-end workflow functional
- [ ] At least one segment created successfully

### **Comprehensive Testing**
- [ ] All test scenarios pass
- [ ] Error handling verified
- [ ] Performance acceptable
- [ ] User experience smooth

### **Production Ready**
- [ ] 100% test success rate
- [ ] No critical errors
- [ ] Performance benchmarks met
- [ ] Security verified

---

## 🚀 **Next Steps After Testing**

1. **If All Tests Pass:**
   - Deploy to production
   - Add advanced features
   - Implement monitoring

2. **If Some Tests Fail:**
   - Investigate failures
   - Fix identified issues
   - Re-run tests

3. **If Critical Issues Found:**
   - Document problems
   - Prioritize fixes
   - Re-test after fixes

---

## 📞 **Getting Help**

### **Debug Information**
- Check terminal output for error messages
- Review Streamlit app logs
- Verify Adobe Analytics API responses

### **Common Commands**
```bash
# Check app status
ps aux | grep streamlit

# View logs
tail -f ~/.streamlit/logs/streamlit.log

# Test specific function
python -c "from app import detect_create_action; print(detect_create_action('test'))"
```

---

**Happy Testing! 🎉**

The application is designed to be robust and user-friendly. If you encounter any issues, the error handling system should provide clear guidance on how to resolve them. 