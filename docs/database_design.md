# モンクモード支援システム - データベース設計書

## 概要
- データベース: Supabase (PostgreSQL)
- 認証: Supabase Auth
- セキュリティ: Row Level Security (RLS) 有効化

---

## テーブル定義

### 1. user_profiles
ユーザーの追加プロフィール情報

```sql
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name VARCHAR(100),
  monk_mode_start_date DATE,
  monk_mode_end_date DATE,
  monk_mode_duration_days INTEGER,
  target_wake_time TIME DEFAULT '07:00:00',
  target_sleep_time TIME DEFAULT '23:00:00',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS ポリシー
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile"
  ON user_profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile"
  ON user_profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
  ON user_profiles FOR UPDATE
  USING (auth.uid() = id);

-- サインアップ時に自動的にプロフィールを作成するトリガー
-- SECURITY DEFINER によりRLSをバイパスして実行される
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (id, display_name)
  VALUES (NEW.id, COALESCE(NEW.raw_user_meta_data->>'display_name', ''));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

---

### 2. daily_tasks
デイリータスク管理

```sql
CREATE TABLE daily_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  category VARCHAR(50), -- '運動', '学習', '健康管理', '自己研鑽', 'その他'
  priority VARCHAR(20) DEFAULT 'medium', -- 'high', 'medium', 'low'
  is_completed BOOLEAN DEFAULT FALSE,
  task_date DATE NOT NULL DEFAULT CURRENT_DATE,
  completed_at TIMESTAMP WITH TIME ZONE,
  display_order INTEGER DEFAULT 0,
  routine_id UUID REFERENCES routines(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_daily_tasks_user_date ON daily_tasks(user_id, task_date);
CREATE INDEX idx_daily_tasks_completed ON daily_tasks(user_id, is_completed);

-- RLS ポリシー
ALTER TABLE daily_tasks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own tasks"
  ON daily_tasks FOR ALL
  USING (auth.uid() = user_id);
```

---

### 3. routines
ルーティンテンプレート

```sql
CREATE TABLE routines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  category VARCHAR(50),
  frequency VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly'
  weekdays INTEGER[], -- 週単位の場合: [0,1,2,3,4,5,6] (0=日曜)
  month_day INTEGER, -- 月単位の場合: 1-31
  recommended_duration_minutes INTEGER,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_routines_user ON routines(user_id);
CREATE INDEX idx_routines_active ON routines(user_id, is_active);

-- RLS ポリシー
ALTER TABLE routines ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own routines"
  ON routines FOR ALL
  USING (auth.uid() = user_id);
```

---

### 4. habit_records
日々の習慣記録

```sql
CREATE TABLE habit_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  record_date DATE NOT NULL DEFAULT CURRENT_DATE,
  
  -- 必須習慣（実施チェック）
  sleep_hours DECIMAL(3,1), -- 睡眠時間
  exercise_done BOOLEAN DEFAULT FALSE,
  meditation_done BOOLEAN DEFAULT FALSE,
  reading_minutes INTEGER DEFAULT 0,
  water_intake_liters DECIMAL(3,1) DEFAULT 0,
  sunlight_done BOOLEAN DEFAULT FALSE,
  cold_shower_done BOOLEAN DEFAULT FALSE,
  
  -- 禁止事項達成チェック
  no_porn_achieved BOOLEAN DEFAULT TRUE,
  no_short_videos_achieved BOOLEAN DEFAULT TRUE,
  no_junk_food_achieved BOOLEAN DEFAULT TRUE,
  no_alcohol_tobacco_achieved BOOLEAN DEFAULT TRUE,
  screen_time_minutes INTEGER DEFAULT 0, -- 2-3時間以内が目標
  
  -- その他
  mood_rating INTEGER CHECK (mood_rating >= 1 AND mood_rating <= 5),
  notes TEXT,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  UNIQUE(user_id, record_date)
);

CREATE INDEX idx_habit_records_user_date ON habit_records(user_id, record_date DESC);

-- RLS ポリシー
ALTER TABLE habit_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own habit records"
  ON habit_records FOR ALL
  USING (auth.uid() = user_id);
```

---

### 5. journals
日記（ジャーナリング）

```sql
CREATE TABLE journals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  journal_date DATE NOT NULL DEFAULT CURRENT_DATE,
  
  -- 振り返りプロンプトへの回答
  achievements TEXT, -- 今日達成できたこと
  improvements TEXT, -- 改善すべき点
  learnings TEXT, -- 気づきや学び
  tomorrow_priority TEXT, -- 明日の最優先事項
  gratitude TEXT, -- 感謝すること3つ
  
  -- フリーフォーム日記
  free_text TEXT,
  
  mood_rating INTEGER CHECK (mood_rating >= 1 AND mood_rating <= 5),
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  UNIQUE(user_id, journal_date)
);

CREATE INDEX idx_journals_user_date ON journals(user_id, journal_date DESC);

-- RLS ポリシー
ALTER TABLE journals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own journals"
  ON journals FOR ALL
  USING (auth.uid() = user_id);
```

---

### 6. pomodoro_sessions
ポモドーロタイマーセッション記録

```sql
CREATE TABLE pomodoro_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  task_id UUID REFERENCES daily_tasks(id) ON DELETE SET NULL,
  
  session_type VARCHAR(20) NOT NULL, -- 'work', 'short_break', 'long_break'
  duration_minutes INTEGER NOT NULL,
  started_at TIMESTAMP WITH TIME ZONE NOT NULL,
  ended_at TIMESTAMP WITH TIME ZONE,
  completed BOOLEAN DEFAULT FALSE,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_pomodoro_user_date ON pomodoro_sessions(user_id, started_at DESC);
CREATE INDEX idx_pomodoro_task ON pomodoro_sessions(task_id);

-- RLS ポリシー
ALTER TABLE pomodoro_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own pomodoro sessions"
  ON pomodoro_sessions FOR ALL
  USING (auth.uid() = user_id);
```

---

### 7. weekly_reviews
週次振り返り

```sql
CREATE TABLE weekly_reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  week_start_date DATE NOT NULL,
  week_end_date DATE NOT NULL,
  
  what_went_well TEXT, -- うまくいったこと
  what_to_improve TEXT, -- 改善点
  next_week_priority TEXT, -- 翌週の最優先事項
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  UNIQUE(user_id, week_start_date)
);

CREATE INDEX idx_weekly_reviews_user ON weekly_reviews(user_id, week_start_date DESC);

-- RLS ポリシー
ALTER TABLE weekly_reviews ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own weekly reviews"
  ON weekly_reviews FOR ALL
  USING (auth.uid() = user_id);
```

---

### 8. notification_settings
通知設定

```sql
CREATE TABLE notification_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- 各種通知のON/OFF
  task_reminders_enabled BOOLEAN DEFAULT TRUE,
  routine_reminders_enabled BOOLEAN DEFAULT TRUE,
  sleep_reminder_enabled BOOLEAN DEFAULT TRUE,
  water_reminder_enabled BOOLEAN DEFAULT TRUE,
  
  -- 通知時刻設定
  sleep_reminder_time TIME DEFAULT '22:30:00',
  water_reminder_interval_hours INTEGER DEFAULT 2,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  UNIQUE(user_id)
);

-- RLS ポリシー
ALTER TABLE notification_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own notification settings"
  ON notification_settings FOR ALL
  USING (auth.uid() = user_id);
```

---

## 初期データ（モンクモード推奨ルーティンテンプレート）

```sql
-- システムユーザーとして推奨ルーティンを作成（各ユーザーがコピーして使用）
-- 実装時に管理画面から登録、またはユーザー作成時にコピー機能を提供
```

---

## インデックス戦略

- **user_id + date**: ほぼ全テーブルで日付範囲検索が頻繁
- **completed/active状態**: フィルタリング頻度が高い
- **外部キー**: JOINパフォーマンス向上

---

## セキュリティポリシー

全テーブルで以下を徹底:
1. RLS有効化
2. auth.uid()による所有者チェック
3. CASCADE DELETE設定（ユーザー削除時のデータ整合性）

---

## バックアップ戦略

- Supabaseの自動バックアップ機能を使用
- データエクスポート機能（CSV/JSON）をアプリ側で実装

---

## 次のステップ

1. Supabaseプロジェクト作成
2. 上記SQLの実行
3. RLSポリシーの動作確認
4. テストデータ投入
