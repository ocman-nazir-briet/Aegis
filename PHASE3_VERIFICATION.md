# Phase 3: Developer Tooling — Verification

This document outlines the verification steps for Phase 3 implementation.

## Files Created

### Backend
- `backend/app/api/routes.py` - Added `GET /pr/{pr_id}/analysis` endpoint

### VS Code Extension
- `vscode-extension/package.json` - Extension manifest
- `vscode-extension/tsconfig.json` - TypeScript configuration
- `vscode-extension/src/extension.ts` - Extension activation and command wiring
- `vscode-extension/src/aegisClient.ts` - HTTP client for API calls
- `vscode-extension/src/decorations.ts` - Text editor decorations and diagnostics
- `vscode-extension/src/statusBar.ts` - Status bar management
- `vscode-extension/src/sidebar.ts` - WebviewView provider for risk panel

### GitHub Actions
- `.github/workflows/aegis-pr-check.yml` - CI/CD workflow for automated PR checks

## Backend Verification

### Step 1: Check PR Analysis Route
The new route at `GET /api/v1/pr/{pr_id}/analysis` should:
1. Accept a PR ID as a path parameter
2. Query Neo4j for ChangeEvent nodes matching the PR
3. Return the most recent analysis or 404 if not found

**Test:**
```bash
curl http://localhost:8000/api/v1/pr/12345/analysis
```

Expected response (if no analysis exists):
```json
{
  "success": false,
  "error": "No analysis found for PR 12345"
}
```

After running a simulation, re-run the same curl command to retrieve the cached analysis.

## VS Code Extension Verification

### Step 1: Build the Extension
```bash
cd vscode-extension
npm install
npm run compile
```

This should produce compiled output in `out/` directory without TypeScript errors.

### Step 2: Load in Extension Development Host

In VS Code:
1. Open the `vscode-extension` folder in a new window
2. Press `F5` to launch "Extension Development Host"
3. A new VS Code window opens with the extension loaded

### Step 3: Test Status Bar
1. The status bar should show: `$(shield) Aegis: Idle`
2. Open a file in the editor
3. Make an edit and save
4. Status bar should briefly show: `$(sync~spin) Aegis: Analyzing...`
5. After response, should show: `$(shield) Aegis: Low 🟢` (or appropriate risk level)

### Step 4: Test Sidebar Panel
1. Click the Aegis icon in the activity bar (left sidebar)
2. Should show "👈 Save a file to see risk analysis"
3. After running analysis, sidebar should populate with:
   - Risk badge (color-coded)
   - Confidence percentage with bar
   - Blast radius (services, endpoints, databases)
   - Predicted impact metrics
   - Analysis explanation
   - Mitigation list
   - Affected entities

### Step 5: Test Command Palette
1. Press `Cmd+Shift+P` (or `Ctrl+Shift+P` on Linux/Windows)
2. Type "Aegis" to see available commands:
   - `Aegis Twin: Run Aegis Simulation`
   - `Aegis Twin: Open Aegis Dashboard`
   - `Aegis Twin: Clear Risk Decorations`
3. Run "Run Aegis Simulation" and verify it triggers analysis

### Step 6: Test Decorations
After running analysis on a file with changes:
- Low/Medium risk: Changed lines should have yellow left border
- High/Critical risk: Changed lines should have red background
- High/Critical risk: Issues should appear in Problems panel

### Step 7: Test Configuration
In the dev extension window:
1. Open Settings (`Cmd+,` / `Ctrl+,`)
2. Search for "aegis"
3. Verify these settings are visible:
   - `aegisTwin.apiUrl` - default `http://localhost:8000`
   - `aegisTwin.repoUrl` - default empty (auto-detect)
   - `aegisTwin.autoAnalyzeOnSave` - default `true`
4. Try toggling `autoAnalyzeOnSave` and verify on-save behavior changes

### Step 8: Test Dashboard Link
1. Run "Open Aegis Dashboard" from command palette
2. Should open `http://localhost:3000` in browser
3. If port differs, adjust the URL translation in extension.ts

## GitHub Actions Verification

### Step 1: Workflow File Validation
The workflow file should be syntactically valid YAML:
```bash
cd .github/workflows
cat aegis-pr-check.yml
```

Key validation:
- Job name: `risk-analysis`
- Triggers: `pull_request` with types `[opened, synchronize]`
- Steps include:
  - Checkout code
  - Get diff
  - Call Aegis API
  - Post PR comment
  - Block on Critical

### Step 2: Configure Repository Variable
Before testing:
1. Go to GitHub repo Settings → Secrets and variables → Actions
2. Create a **repository variable** (not secret):
   - Name: `AEGIS_API_URL`
   - Value: `http://your-api-host:8000` or `https://api.aegis.internal`

Note: If not configured, the action will skip with a warning.

### Step 3: Test Workflow (Dry Run)
Create a test PR with minor changes:
1. Create a new branch: `git checkout -b test-aegis`
2. Make a small change to a file
3. Commit and push
4. Create a pull request
5. Monitor Actions tab for workflow run
6. Workflow should:
   - ✅ Checkout code
   - ✅ Get diff
   - ✅ Call Aegis API (or show warning if API_URL not set)
   - ✅ Post comment on PR if API succeeded
   - ✅ Set commit status

### Step 4: Test Critical Risk Blocking
If configured with API running:
1. Create a PR with significant changes (expected to trigger Critical risk)
2. Workflow should:
   - ✅ Post comment with 🔴 Critical badge
   - ✅ Fail the job with message "Merge blocked"
   - ✅ Prevent merge until analysis is resolved

### Step 5: Test Comment Quality
PR comment should include:
- Header: "🛡️ Aegis Twin — Risk Analysis"
- Risk badge with confidence percentage
- Blast radius table (services, endpoints, databases)
- Analysis explanation text
- Numbered mitigation list
- Affected entities (if available)

## Integration Test

### End-to-End Flow
1. **Backend running**: `python -m uvicorn backend.main:app --reload --port 8000`
2. **Frontend running**: `cd frontend && npm start` (port 3000)
3. **Neo4j running**: Docker container from Phase 1 setup
4. **VS Code extension**: Loaded in Extension Development Host
5. **Repository**: Git repo with some sample code

**Test sequence:**
1. Edit a file in the extension dev window
2. Save the file
3. Extension should:
   - Show "Analyzing..." status
   - Call backend `/api/v1/simulate/change`
   - Receive risk assessment
   - Apply decorations
   - Update sidebar
   - Show notification for High/Critical
4. Navigate to localhost:3000 to verify same data appears in frontend
5. Verify PR analysis endpoint by direct API call (after simulation)

## Checklist

- [ ] Backend route `/pr/{pr_id}/analysis` works correctly
- [ ] Extension compiles without TypeScript errors
- [ ] Status bar shows appropriate states
- [ ] Sidebar renders risk reports correctly
- [ ] Decorations apply to changed lines
- [ ] Problems panel shows High/Critical issues
- [ ] Command palette commands are registered
- [ ] Configuration settings are accessible
- [ ] Dashboard link navigates correctly
- [ ] GitHub Actions workflow is valid YAML
- [ ] Workflow calls API and posts comments
- [ ] Workflow blocks merge on Critical risk
- [ ] Extension auto-analyzes on file save
- [ ] Extension detects git repo URL automatically
- [ ] API timeout handling works (30s timeout)

## Known Limitations

1. **Git diff retrieval**: Requires VS Code Git extension; will be null if extension not loaded
2. **API reachability**: If API is unreachable, status shows "Error" — user must check localhost:8000
3. **Large diffs**: Diffs over 500KB are truncated by GitHub Actions
4. **Offline mode**: Extension won't function without network access to API
5. **Private repos**: GitHub Actions needs `AEGIS_API_URL` configured for private repos

## Next Steps

After verification passes:
1. Package extension: `vsce package` (requires VS Code Extension Manager)
2. Publish to VS Code Marketplace (optional)
3. Deploy backend to staging environment
4. Test GitHub Actions with real PRs
5. Gather user feedback and iterate
