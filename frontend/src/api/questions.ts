import type { QuestionDetail, QuestionSummary, SubmitResponse } from '../types'

export async function listQuestions(): Promise<QuestionSummary[]> {
  // GET /questions
  throw new Error('not implemented')
}

export async function getQuestion(_id: string): Promise<QuestionDetail> {
  // GET /questions/{id}
  throw new Error('not implemented')
}

export async function submitCode(_id: string, _code: string): Promise<SubmitResponse> {
  // POST /questions/{id}/submit with {code}
  throw new Error('not implemented')
}
