import type { QuestionDetail, QuestionSummary, SubmitResponse } from '../types'
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
