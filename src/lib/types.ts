export interface GrowthRecord {
  id: string;
  date: string; // 改为字符串类型以匹配表单输入
  weight?: number;
  height?: number;
  notes?: string;
  photos: string[];
}

export interface CatProfile {
  id: string;
  name: string;
  age: number;
  breed?: string;
  photos: string[];
}

export interface User {
  id: string;
  name: string;
  avatar?: string;
}
