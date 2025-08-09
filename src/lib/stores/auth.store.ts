import { writable } from 'svelte/store';

export interface AuthState {
    isAuthenticated: boolean;
    token: string | null;
    user: {
        username: string;
        email: string;
    } | null;
}

const initialState: AuthState = {
    isAuthenticated: false,
    token: null,
    user: null
};

export const authStore = writable<AuthState>(initialState);

export async function login(token: string) {
    // 基本验证
    if (!token || typeof token !== 'string') {
        throw new Error('Token不能为空');
    }

    try {
        console.log('Using token:', token);
        
        // 调用API获取用户信息
        const response = await fetch('/api/v1/users/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('获取用户信息失败');
        }

        const result = await response.json();
        
        // 验证API返回数据结构
        if (!result || typeof result !== 'object') {
            throw new Error('无效的API响应格式');
        }

        const userData = result.data || result; // 兼容两种响应格式
        
        authStore.update(state => ({
            ...state,
            isAuthenticated: true,
            token,
            user: {
                username: userData.username || userData.name || 'user',
                email: userData.email || 'user@example.com'
            }
        }));
        localStorage.setItem('authToken', token);
    } catch (err) {
        console.error('登录失败:', err);
        const message = err instanceof Error ? err.message : '未知错误';
        throw new Error('登录失败: ' + message);
    }
}

export function logout() {
    authStore.set(initialState);
    localStorage.removeItem('authToken');
}

export async function initializeAuth() {
    const token = localStorage.getItem('authToken');
    if (token) {
        // 验证token有效性
        try {
            const response = await fetch('/api/v1/users/me', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                if (!result || typeof result !== 'object') {
                    throw new Error('无效的API响应格式');
                }
                await login(token);
                return true;
            }
        } catch (err) {
            console.error('Token验证失败:', err);
        }
    }
    return false;
}
