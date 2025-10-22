<template>
  <div class="requirement-table">
    <div v-if="searchResults" class="cfts-results">
      <h2>{{ searchType === 'req' ? 'Req.ID 搜尋結果' : 'CFTS 搜尋結果' }}</h2>
      <div class="result-summary">
        <div class="summary-item">
          <strong>CFTS ID:</strong> {{ searchResults.cfts_id }}
        </div>
        <div class="summary-item">
          <strong>總筆數:</strong> {{ searchResults.total_count }} 筆
        </div>
        <div v-if="searchResults.target_req_id" class="summary-item">
          <strong>目標 Req.ID:</strong> {{ searchResults.target_req_id }}
        </div>
      </div>


      <div class="table-container">
        <table class="excel-table">
          <thead>
            <tr>
              <th>SR26 Description</th>
              <th>ReqIF.ForeignID</th>
              <th>Source Id</th>
              <th>SR24 Description</th>
              <th>Melco Id</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(requirement, index) in filteredRequirements"
              :key="requirement.req_id"
              :class="{
                'even-row': index % 2 === 1,
                'target-row': requirement.req_id === searchResults.target_req_id
              }"
              :ref="el => assignTargetRowRef(el, requirement.req_id)"
              :data-req-id="requirement.req_id"
            >
              <td class="sr26-description">
                <div class="sr26-wrapper">
                  <span
                    v-if="hasSrDifference(requirement.description, requirement.sr24_description)"
                    class="sr26-diff-badge"
                  >
                    與 SR24 不同
                  </span>
                  <div
                    class="sr26-content"
                    v-html="highlightDifferences(requirement.description, requirement.sr24_description)"
                  ></div>
                </div>
              </td>
              <td class="reqif-foreign-id">{{ requirement.req_id }}</td>
              <td class="source-id">
                {{ requirement.source_id || '' }}
              </td>
              <td class="sr24-description">{{ requirement.sr24_description || '' }}</td>
              <td class="melco-id">
                <template v-if="requirement.melco_id">
                  <div v-for="(melcoId, idx) in splitMelcoIds(requirement.melco_id)" :key="idx" class="melco-id-item">
                    <a
                      v-if="isMelcoIdAvailable(melcoId)"
                      @click.prevent="viewMelcoDetail(melcoId)"
                      class="melco-link"
                      :title="`點擊查看 ${melcoId} 的 SYS.2 詳細資訊`"
                    >
                      {{ melcoId }}
                    </a>
                    <span
                      v-else
                      class="melco-text"
                      :title="`${melcoId} 沒有 SYS.2 資料`"
                    >
                      {{ melcoId }}
                    </span>
                  </div>
                </template>
                <span v-else>-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else-if="searchResults === null" class="no-results">
      <p>請使用上方搜尋欄進行搜尋</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RequirementTable',
  props: {
    searchResults: {
      type: [Object, null],
      default: null
    },
    searchType: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      melcoIdAvailability: {}, // Store which Melco IDs have SYS.2 data
      targetRowEl: null
    }
  },
  computed: {
    filteredRequirements() {
      if (!this.searchResults || !this.searchResults.requirements) {
        return []
      }
      return this.searchResults.requirements
    }
  },
  watch: {
    searchResults: {
      immediate: true,
      async handler(newVal) {
        this.targetRowEl = null
        if (newVal && newVal.requirements) {
          await this.checkMelcoIdAvailability()

          if (newVal.target_req_id) {
            this.scrollToTargetRow()
          }
        }
      }
    }
  },
  methods: {
    assignTargetRowRef(el, reqId) {
      if (!this.searchResults || reqId !== this.searchResults.target_req_id) {
        if (!el && this.targetRowEl && this.targetRowEl.dataset?.reqId === reqId) {
          this.targetRowEl = null
        }
        return
      }
      if (el) {
        el.dataset.reqId = reqId
        this.targetRowEl = el
      }
    },
    scrollToTargetRow() {
      this.$nextTick(() => {
        if (this.targetRowEl && typeof this.targetRowEl.scrollIntoView === 'function') {
          this.targetRowEl.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
          })
        }
      })
    },
    async checkMelcoIdAvailability() {
      // Collect all unique Melco IDs from search results
      const melcoIds = new Set()

      this.searchResults.requirements.forEach(req => {
        if (req.melco_id) {
          this.splitMelcoIds(req.melco_id).forEach(id => {
            if (id) melcoIds.add(id)
          })
        }
      })

      if (melcoIds.size === 0) {
        this.melcoIdAvailability = {}
        return
      }

      const searchParams = new URLSearchParams()
      searchParams.set('ids', Array.from(melcoIds).join(','))

      try {
        const response = await fetch(`/api/sys2/availability?${searchParams.toString()}`)
        if (!response.ok) {
          throw new Error('Failed to load SYS.2 availability')
        }

        const data = await response.json()
        const availability = {}
        melcoIds.forEach(id => {
          availability[id] = data.available_ids.includes(id)
        })
        this.melcoIdAvailability = availability
      } catch (error) {
        const fallback = {}
        melcoIds.forEach(id => {
          fallback[id] = false
        })
        this.melcoIdAvailability = fallback
      }
    },
    isMelcoIdAvailable(melcoId) {
      return this.melcoIdAvailability[melcoId] === true
    },
    viewMelcoDetail(melcoId) {
      // Clean the Melco ID before emitting (already cleaned by splitMelcoIds, but ensure it's clean)
      const cleanedId = melcoId.trim().replace(/^#+|#+$/g, '')
      this.$emit('view-melco-detail', cleanedId)
    },
    splitMelcoIds(melcoIdString) {
      // Split by newline or comma, clean # symbols, and filter out empty strings
      if (!melcoIdString) return []
      return melcoIdString
        .split(/[\n,]+/)
        .map(id => id.trim().replace(/^#+|#+$/g, ''))  // Remove leading/trailing # symbols
        .filter(id => id.length > 0)
    },
    highlightDifferences(sr26Text, sr24Text) {
      const sr26 = this.normalizeForDiff(sr26Text)
      if (!sr26) return ''

      const sr24 = this.normalizeForDiff(sr24Text)

      if (!sr24) {
        return `<span class="text-added">${this.escapeHtml(sr26)}</span>`
      }

      if (sr26 === sr24) {
        return this.escapeHtml(sr26)
      }

      const sr26Tokens = this.tokenizeText(sr26)
      const sr24Tokens = this.tokenizeText(sr24)

      const sr26WordInfo = this.extractWordTokens(sr26Tokens)
      const sr24WordInfo = this.extractWordTokens(sr24Tokens)

      const maxWordCount = 600
      if (
        sr26WordInfo.words.length > maxWordCount ||
        sr24WordInfo.words.length > maxWordCount
      ) {
        return `<span class="text-added">${this.escapeHtml(sr26)}</span>`
      }

      const matchedWords = this.longestCommonSubsequence(
        sr24WordInfo.words,
        sr26WordInfo.words
      )

      const matchedSr26TokenIndexes = new Set(
        matchedWords.map(match => sr26WordInfo.wordToTokenIndex[match.targetIndex])
      )

      let highlighted = ''
      sr26Tokens.forEach((token, index) => {
        const escapedToken = this.escapeHtml(token)
        if (token.trim() === '') {
          highlighted += escapedToken
        } else if (
          sr26WordInfo.tokenTypes[index] === 'word' &&
          !matchedSr26TokenIndexes.has(index)
        ) {
          highlighted += `<span class="text-added">${escapedToken}</span>`
        } else {
          highlighted += escapedToken
        }
      })

      return highlighted
    },
    hasSrDifference(sr26Text, sr24Text) {
      const sr26 = this.normalizeForDiff(sr26Text)
      if (!sr26) return false
      const sr24 = this.normalizeForDiff(sr24Text)
      if (!sr24) return true
      if (sr26 === sr24) return false

      const sr26Tokens = this.tokenizeText(sr26)
      const sr24Tokens = this.tokenizeText(sr24)
      const sr26WordInfo = this.extractWordTokens(sr26Tokens)
      const sr24WordInfo = this.extractWordTokens(sr24Tokens)

      if (sr26WordInfo.words.length === 0 && sr24WordInfo.words.length === 0) {
        return false
      }

      const matches = this.longestCommonSubsequence(
        sr24WordInfo.words,
        sr26WordInfo.words
      )

      return !(
        matches.length === sr26WordInfo.words.length &&
        matches.length === sr24WordInfo.words.length
      )
    },
    normalizeForDiff(text) {
      if (!text) return ''
      return String(text).replace(/\r\n/g, '\n')
    },
    tokenizeText(text) {
      return text.match(/\s+|\S+/g) || []
    },
    extractWordTokens(tokens) {
      const words = []
      const wordToTokenIndex = []
      const tokenTypes = []

      tokens.forEach((token, index) => {
        if (token.trim() === '') {
          tokenTypes[index] = 'whitespace'
          return
        }

        tokenTypes[index] = 'word'
        wordToTokenIndex.push(index)
        words.push(token)
      })

      return { words, wordToTokenIndex, tokenTypes }
    },
    longestCommonSubsequence(sourceWords, targetWords) {
      const m = sourceWords.length
      const n = targetWords.length
      const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0))

      for (let i = m - 1; i >= 0; i--) {
        for (let j = n - 1; j >= 0; j--) {
          if (sourceWords[i] === targetWords[j]) {
            dp[i][j] = dp[i + 1][j + 1] + 1
          } else {
            dp[i][j] = Math.max(dp[i + 1][j], dp[i][j + 1])
          }
        }
      }

      const matches = []
      let i = 0
      let j = 0

      while (i < m && j < n) {
        if (sourceWords[i] === targetWords[j]) {
          matches.push({ sourceIndex: i, targetIndex: j })
          i += 1
          j += 1
        } else if (dp[i + 1][j] >= dp[i][j + 1]) {
          i += 1
        } else {
          j += 1
        }
      }

      return matches
    },
    escapeHtml(text) {
      const div = document.createElement('div')
      div.textContent = text
      return div.innerHTML
    }
  }
}
</script>

<style scoped>
.requirement-table {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

/* SR26 difference highlighting */
.sr26-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sr26-diff-badge {
  align-self: flex-start;
  background: #fbbf24;
  color: #92400e;
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 9999px;
  letter-spacing: 0.02em;
}

.sr26-content {
  white-space: pre-wrap;
}

:deep(.text-added) {
  background-color: #fef3c7;
  padding: 2px 0;
  border-radius: 2px;
  box-shadow: inset 0 -1px 0 0 rgba(251, 191, 36, 0.4);
  color: #92400e;
}

.cfts-results, .req-results {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

h2 {
  color: #1f2937;
  padding: 20px 24px;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.result-summary {
  display: flex;
  gap: 24px;
  padding: 16px 24px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.summary-item {
  font-size: 14px;
  color: #6b7280;
}

.summary-item strong {
  color: #374151;
  font-weight: 600;
  margin-right: 8px;
}

.table-container {
  overflow-x: auto;
}

.excel-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.excel-table th {
  background: #f9fafb;
  color: #374151;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #e5e7eb;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  position: sticky;
  top: 0;
  z-index: 10;
}

.excel-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: top;
  color: #1f2937;
  line-height: 1.5;
}

.excel-table tbody tr {
  transition: background-color 0.15s ease;
}

.excel-table tbody tr:hover {
  background: #f3f4f6;
}

.sr24-description,
.sr26-description {
  min-width: 250px;
  max-width: 400px;
  word-wrap: break-word;
}

.source-id {
  min-width: 140px;
  text-align: center;
  color: #6b7280;
  white-space: nowrap;
}

.source-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.15s ease;
}

.source-link:hover {
  color: #2563eb;
  text-decoration: underline;
}

.reqif-foreign-id {
  font-weight: 500;
  color: #059669;
  min-width: 100px;
  text-align: center;
}

.melco-id {
  min-width: 150px;
  text-align: center;
  vertical-align: top;
}

.melco-id-item {
  margin: 2px 0;
}

.melco-link {
  color: #7c3aed;
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
  white-space: nowrap;
}

.melco-link:hover {
  color: #6d28d9;
  background: #ede9fe;
  text-decoration: none;
}

.melco-text {
  color: #9ca3af;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
  white-space: nowrap;
  cursor: default;
}

.no-results {
  text-align: center;
  color: #6b7280;
  font-size: 14px;
  padding: 48px 24px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.target-row {
  background: #e6fffb !important;
  border-left: 3px solid #14b8a6;
}

.target-row td {
  font-weight: 600;
  color: #075985;
}

@media (max-width: 768px) {
  .requirement-table {
    padding: 16px;
  }

  .result-summary {
    flex-direction: column;
    gap: 12px;
  }

  .excel-table {
    font-size: 12px;
  }

  .excel-table th,
  .excel-table td {
    padding: 10px 12px;
  }
}
</style>
