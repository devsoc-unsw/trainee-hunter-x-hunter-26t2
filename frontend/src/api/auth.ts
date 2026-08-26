import type { TokenResponse } from '../types'

export async function signup(_username: string, _password: string): Promise<TokenResponse> {
  // POST /auth/signup with apiPost
  throw new Error('not implemented')
}

export async function login(_username: string, _password: string): Promise<TokenResponse> {
  // POST /auth/login
  throw new Error('not implemented')
}

export async function logout(): Promise<void> {
  // POST /auth/logout
  throw new Error('not implemented')
}
