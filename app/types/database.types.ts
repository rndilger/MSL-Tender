export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      admin_users: {
        Row: {
          id: string
          email: string
          full_name: string | null
          role: string
          is_active: boolean
          added_at: string
          added_by: string | null
          last_login: string | null
        }
        Insert: {
          id: string
          email: string
          full_name?: string | null
          role?: string
          is_active?: boolean
          added_at?: string
          added_by?: string | null
          last_login?: string | null
        }
        Update: {
          id?: string
          email?: string
          full_name?: string | null
          role?: string
          is_active?: boolean
          added_at?: string
          added_by?: string | null
          last_login?: string | null
        }
      }
      experiments: {
        Row: {
          id: string
          name: string
          description: string | null
          created_by: string
          created_at: string
          status: string
          participant_instructions: string | null
          shuffle_samples: boolean
          samples_per_set: number
        }
        Insert: {
          id?: string
          name: string
          description?: string | null
          created_by: string
          created_at?: string
          status?: string
          participant_instructions?: string | null
          shuffle_samples?: boolean
          samples_per_set?: number
        }
        Update: {
          id?: string
          name?: string
          description?: string | null
          created_by?: string
          created_at?: string
          status?: string
          participant_instructions?: string | null
          shuffle_samples?: boolean
          samples_per_set?: number
        }
      }
      pork_samples: {
        Row: {
          id: string
          study_number: number
          original_chop_id: string
          standardized_chop_id: string
          block: number | null
          days_display: number | null
          shelf_life: number | null
          slice_method: string | null
          enhancement_level: string | null
          case_life: string | null
          instrument_shear_value: number | null
          instrument_shear_units: string | null
          trained_panel_tenderness: number | null
          trained_panel_juiciness: number | null
          trained_panel_pork_flavor: number | null
          trained_panel_off_flavor: number | null
          consumer_overall_like: number | null
          consumer_tenderness_like: number | null
          consumer_juiciness_like: number | null
          consumer_flavor_like: number | null
          consumer_overall_quality: number | null
          notes: string | null
        }
        Insert: {
          id?: string
          study_number: number
          original_chop_id: string
          standardized_chop_id: string
          block?: number | null
          days_display?: number | null
          shelf_life?: number | null
          slice_method?: string | null
          enhancement_level?: string | null
          case_life?: string | null
          instrument_shear_value?: number | null
          instrument_shear_units?: string | null
          trained_panel_tenderness?: number | null
          trained_panel_juiciness?: number | null
          trained_panel_pork_flavor?: number | null
          trained_panel_off_flavor?: number | null
          consumer_overall_like?: number | null
          consumer_tenderness_like?: number | null
          consumer_juiciness_like?: number | null
          consumer_flavor_like?: number | null
          consumer_overall_quality?: number | null
          notes?: string | null
        }
        Update: {
          id?: string
          study_number?: number
          original_chop_id?: string
          standardized_chop_id?: string
          block?: number | null
          days_display?: number | null
          shelf_life?: number | null
          slice_method?: string | null
          enhancement_level?: string | null
          case_life?: string | null
          instrument_shear_value?: number | null
          instrument_shear_units?: string | null
          trained_panel_tenderness?: number | null
          trained_panel_juiciness?: number | null
          trained_panel_pork_flavor?: number | null
          trained_panel_off_flavor?: number | null
          consumer_overall_like?: number | null
          consumer_tenderness_like?: number | null
          consumer_juiciness_like?: number | null
          consumer_flavor_like?: number | null
          consumer_overall_quality?: number | null
          notes?: string | null
        }
      }
      participant_sessions: {
        Row: {
          id: string
          experiment_id: string
          participant_name: string
          email: string | null
          started_at: string
          completed_at: string | null
          ip_address: string | null
        }
        Insert: {
          id?: string
          experiment_id: string
          participant_name: string
          email?: string | null
          started_at?: string
          completed_at?: string | null
          ip_address?: string | null
        }
        Update: {
          id?: string
          experiment_id?: string
          participant_name?: string
          email?: string | null
          started_at?: string
          completed_at?: string | null
          ip_address?: string | null
        }
      }
      responses: {
        Row: {
          id: string
          session_id: string
          set_number: number
          selected_sample_id: string
          response_time_ms: number | null
          created_at: string
        }
        Insert: {
          id?: string
          session_id: string
          set_number: number
          selected_sample_id: string
          response_time_ms?: number | null
          created_at?: string
        }
        Update: {
          id?: string
          session_id?: string
          set_number?: number
          selected_sample_id?: string
          response_time_ms?: number | null
          created_at?: string
        }
      }
      sample_images: {
        Row: {
          id: string
          sample_id: string
          storage_path: string
          image_type: string
          uploaded_at: string
        }
        Insert: {
          id?: string
          sample_id: string
          storage_path: string
          image_type?: string
          uploaded_at?: string
        }
        Update: {
          id?: string
          sample_id?: string
          storage_path?: string
          image_type?: string
          uploaded_at?: string
        }
      }
      experiment_samples: {
        Row: {
          id: string
          experiment_id: string
          sample_id: string
          display_order: number | null
          set_number: number | null
        }
        Insert: {
          id?: string
          experiment_id: string
          sample_id: string
          display_order?: number | null
          set_number?: number | null
        }
        Update: {
          id?: string
          experiment_id?: string
          sample_id?: string
          display_order?: number | null
          set_number?: number | null
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      is_admin: {
        Args: Record<PropertyKey, never>
        Returns: boolean
      }
    }
    Enums: {
      [_ in never]: never
    }
  }
}
