/*
  # Complete User Management System

  1. New Tables
    - `users` - User accounts with subscription management
    - `user_activity` - Track all user actions for analytics
    - `password_resets` - Handle password reset tokens
    - `feedback` - User feedback and support
    - `search_logs` - Product search history
    - `orders` - Order management
    - `order_items` - Individual order items
    - `product_suggestions` - AI-generated suggestions
    - `custom_branding` - User branding preferences

  2. Security
    - Enable RLS on all tables
    - Add policies for user data access
    - Admin-only access for management tables

  3. Analytics
    - Comprehensive activity tracking
    - Subscription analytics
    - User behavior insights
*/

-- Users table with subscription management
CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  username text UNIQUE NOT NULL,
  email text UNIQUE NOT NULL,
  password_hash text NOT NULL,
  subscription_tier text DEFAULT 'basic' CHECK (subscription_tier IN ('basic', 'premium', 'enterprise')),
  subscription_status text DEFAULT 'active' CHECK (subscription_status IN ('active', 'inactive', 'suspended')),
  subscription_start_date timestamptz DEFAULT now(),
  subscription_end_date timestamptz,
  is_admin boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  last_login timestamptz,
  profile_data jsonb DEFAULT '{}'::jsonb
);

-- User activity tracking
CREATE TABLE IF NOT EXISTS user_activity (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  action_type text NOT NULL,
  details jsonb DEFAULT '{}'::jsonb,
  ip_address inet,
  user_agent text,
  created_at timestamptz DEFAULT now()
);

-- Password reset tokens
CREATE TABLE IF NOT EXISTS password_resets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  reset_token text UNIQUE NOT NULL,
  expires_at timestamptz NOT NULL,
  used boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

-- Enhanced feedback table
CREATE TABLE IF NOT EXISTS feedback (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  feedback_text text NOT NULL,
  rating integer CHECK (rating >= 1 AND rating <= 5),
  category text DEFAULT 'general',
  status text DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'flagged')),
  admin_response text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Enhanced search logs
CREATE TABLE IF NOT EXISTS search_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  search_query text NOT NULL,
  search_type text DEFAULT 'product',
  results_count integer DEFAULT 0,
  filters_applied jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

-- Orders management
CREATE TABLE IF NOT EXISTS orders (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  order_number text UNIQUE NOT NULL,
  status text DEFAULT 'draft' CHECK (status IN ('draft', 'pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
  total_amount decimal(10,2) DEFAULT 0,
  currency text DEFAULT 'USD',
  shipping_address jsonb,
  billing_address jsonb,
  notes text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Order items
CREATE TABLE IF NOT EXISTS order_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id uuid REFERENCES orders(id) ON DELETE CASCADE,
  product_name text NOT NULL,
  product_description text,
  quantity integer NOT NULL DEFAULT 1,
  unit_price decimal(10,2) NOT NULL,
  total_price decimal(10,2) NOT NULL,
  product_data jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

-- AI product suggestions
CREATE TABLE IF NOT EXISTS product_suggestions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  industry_segment text NOT NULL,
  prompt text NOT NULL,
  suggestion_data jsonb NOT NULL,
  image_url text,
  custom_branding_applied boolean DEFAULT false,
  rating integer CHECK (rating >= 1 AND rating <= 5),
  created_at timestamptz DEFAULT now()
);

-- Custom branding preferences
CREATE TABLE IF NOT EXISTS custom_branding (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  brand_name text,
  logo_url text,
  primary_color text DEFAULT '#000000',
  secondary_color text DEFAULT '#ffffff',
  font_family text DEFAULT 'Arial',
  brand_guidelines jsonb DEFAULT '{}'::jsonb,
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Social media trends tracking
CREATE TABLE IF NOT EXISTS social_trends (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  platform text NOT NULL,
  trend_keyword text NOT NULL,
  trend_data jsonb NOT NULL,
  relevance_score decimal(3,2) DEFAULT 0,
  industry_tags text[] DEFAULT '{}',
  scraped_at timestamptz DEFAULT now(),
  created_at timestamptz DEFAULT now()
);

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE password_resets ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_suggestions ENABLE ROW LEVEL SECURITY;
ALTER TABLE custom_branding ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_trends ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can read own data" ON users
  FOR SELECT
  USING (id = auth.uid() OR EXISTS (
    SELECT 1 FROM users WHERE id = auth.uid() AND is_admin = true
  ));

CREATE POLICY "Users can update own data" ON users
  FOR UPDATE
  USING (id = auth.uid());

CREATE POLICY "Admins can manage all users" ON users
  FOR ALL
  USING (EXISTS (
    SELECT 1 FROM users WHERE id = auth.uid() AND is_admin = true
  ));

-- Activity policies
CREATE POLICY "Users can read own activity" ON user_activity
  FOR SELECT
  USING (user_id = auth.uid() OR EXISTS (
    SELECT 1 FROM users WHERE id = auth.uid() AND is_admin = true
  ));

CREATE POLICY "System can insert activity" ON user_activity
  FOR INSERT
  WITH CHECK (true);

-- Other table policies (users own data, admins see all)
CREATE POLICY "Own data access" ON feedback
  FOR ALL
  USING (user_id = auth.uid() OR EXISTS (
    SELECT 1 FROM users WHERE id = auth.uid() AND is_admin = true
  ));

CREATE POLICY "Own data access" ON search_logs
  FOR ALL
  USING (user_id = auth.uid() OR EXISTS (
    SELECT 1 FROM users WHERE id = auth.uid() AND is_admin = true
  ));

CREATE POLICY "Own data access" ON orders
  FOR ALL
  USING (user_id = auth.uid() OR EXISTS (
    SELECT 1 FROM users WHERE id = auth.uid() AND is_admin = true
  ));

CREATE POLICY "Own data access" ON product_suggestions
  FOR ALL
  USING (user_id = auth.uid() OR EXISTS (
    SELECT 1 FROM users WHERE id = auth.uid() AND is_admin = true
  ));

CREATE POLICY "Own data access" ON custom_branding
  FOR ALL
  USING (user_id = auth.uid() OR EXISTS (
    SELECT 1 FROM users WHERE id = auth.uid() AND is_admin = true
  ));

-- Admin-only access for social trends
CREATE POLICY "Admin only access" ON social_trends
  FOR ALL
  USING (EXISTS (
    SELECT 1 FROM users WHERE id = auth.uid() AND is_admin = true
  ));

-- Insert admin user and test users
INSERT INTO users (username, email, password_hash, is_admin, subscription_tier) VALUES
('admin', 'admin@procurement.ai', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', true, 'enterprise'),
('testuser1', 'testuser1@example.com', '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5', false, 'basic'),
('testuser2', 'testuser2@example.com', '7c4a8d09ca3762af61e59520943dc26494f8941b', false, 'premium'),
('testuser3', 'testuser3@example.com', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', false, 'enterprise');

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_created_at ON user_activity(created_at);
CREATE INDEX IF NOT EXISTS idx_search_logs_user_id ON search_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id);