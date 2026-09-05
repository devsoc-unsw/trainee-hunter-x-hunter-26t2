import type { KeyDecor } from '../types'
import { apiGet, apiPut, apiDelete } from './client'

export async function getDecor(): Promise<KeyDecor[]> {
    return apiGet<KeyDecor[]>('/keyboard/decor')
}

export async function setSkin(keyChar: string, skinSlug: string | null, keepAccessory = false): Promise<KeyDecor> {
    return apiPut<KeyDecor>(`/keyboard/${keyChar}/skin`, { skin_slug: skinSlug, keep_accessory: keepAccessory })
}

export async function setAccessory(keyChar: string, accessorySlug: string | null): Promise<KeyDecor> {
    return apiPut<KeyDecor>(`/keyboard/${keyChar}/accessory`, { accessory_slug: accessorySlug })
}

export async function clearKey(keyChar: string): Promise<void> {
    return apiDelete<void>(`/keyboard/${keyChar}`)
}