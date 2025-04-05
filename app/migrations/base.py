from typing import List, Dict, Any
from app.core.supabase import supabase_admin

async def create_tables() -> None:
    """Create all necessary tables in Supabase."""
    # Enable pgvector extension
    await supabase_admin.rpc('create_extension', {'name': 'vector'})
    
    # Create tables
    tables = [
        """
        create table if not exists public.profiles (
            id uuid references auth.users on delete cascade primary key,
            full_name text,
            role text check (role in ('admin', 'farmer')),
            created_at timestamp with time zone default timezone('utc'::text, now()),
            updated_at timestamp with time zone default timezone('utc'::text, now())
        )
        """,
        """
        create table if not exists public.devices (
            id uuid default uuid_generate_v4() primary key,
            device_id text unique not null,
            device_type text not null,
            name text,
            description text,
            is_active boolean default true,
            created_at timestamp with time zone default timezone('utc'::text, now())
        )
        """,
        """
        create table if not exists public.farmer_devices (
            id uuid default uuid_generate_v4() primary key,
            farmer_id uuid references public.profiles(id),
            device_id uuid references public.devices(id),
            paired_at timestamp with time zone default timezone('utc'::text, now()),
            unique(farmer_id, device_id)
        )
        """,
        """
        create table if not exists public.scans (
            id uuid default uuid_generate_v4() primary key,
            farmer_id uuid references public.profiles(id),
            device_id uuid references public.devices(id),
            scan_timestamp timestamp with time zone default timezone('utc'::text, now()),
            normal_image_path text,
            thermal_image_path text,
            disease_score float,
            confidence_score float,
            image_embedding vector(512),
            created_at timestamp with time zone default timezone('utc'::text, now())
        )
        """,
        """
        create table if not exists public.soil_readings (
            id uuid default uuid_generate_v4() primary key,
            scan_id uuid references public.scans(id),
            temperature float,
            moisture float,
            ph float,
            nitrogen float,
            phosphorus float,
            potassium float,
            reading_timestamp timestamp with time zone default timezone('utc'::text, now())
        )
        """
    ]
    
    for table_sql in tables:
        await supabase_admin.rpc('execute_sql', {'sql': table_sql})

async def setup_rls() -> None:
    """Set up Row Level Security policies."""
    policies = [
        """
        alter table public.profiles enable row level security;
        """,
        """
        create policy "Users can view their own profile"
            on public.profiles for select
            using (auth.uid() = id);
        """,
        """
        create policy "Users can update their own profile"
            on public.profiles for update
            using (auth.uid() = id);
        """
    ]
    
    for policy_sql in policies:
        await supabase_admin.rpc('execute_sql', {'sql': policy_sql})

async def create_indexes() -> None:
    """Create necessary indexes for performance."""
    indexes = [
        "create index if not exists idx_scans_farmer_id on public.scans(farmer_id);",
        "create index if not exists idx_scans_device_id on public.scans(device_id);",
        "create index if not exists idx_soil_readings_scan_id on public.soil_readings(scan_id);"
    ]
    
    for index_sql in indexes:
        await supabase_admin.rpc('execute_sql', {'sql': index_sql})

async def run_migrations() -> None:
    """Run all migrations in order."""
    await create_tables()
    await setup_rls()
    await create_indexes() 