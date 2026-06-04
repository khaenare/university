export type Role = 'admin' | 'reader';

export interface User {
  id: number;
  username: string;
  role: Role;
}

export interface Publication {
  id: number;
  title: string;
  publisher: string;
  period_months: number;
  price: string;
}

export interface Subscription {
  id: number;
  user_id: number;
  publication_id: number;
  months: number;
  total_amount: string;
  status: string;
  publication: Publication;
}

export interface Payment {
  id: number;
  subscription_id: number;
  amount: string;
  status: string;
}
