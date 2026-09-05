import type { QuestionDetail, QuestionSummary, RunResponse, SubmitResponse } from '../types'
import { apiGet, apiPost } from './client'

export async function listQuestions(): Promise<QuestionSummary[]> {
  // GET /questions
  return apiGet<QuestionSummary[]>('/questions')
}

export async function getQuestion(id: string): Promise<QuestionDetail> {
  // GET /questions/{id}
  return apiGet<QuestionDetail>(`/questions/${id}`)
}

export async function submitCode(id: string, code: string): Promise<SubmitResponse> {
  // POST /questions/{id}/submit with {code}
  return apiPost<SubmitResponse>(`/questions/${id}/submit`, { code })
}

export async function runCode(id: string, code: string): Promise<RunResponse> {
  // POST /questions/{id}/run with {code}. the sample tests only - no coins,
  // no solve recorded. this is the Run button, submitCode is Submit
  return apiPost<RunResponse>(`/questions/${id}/run`, { code })
}
