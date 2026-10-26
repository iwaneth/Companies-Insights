do $$
declare
    target_table text;
    table_names text[] := array[
        'companies',
        'halfDynamicProperties',
        'companyProfile',
        'companyNews'
    ];
begin
    foreach target_table in array table_names loop
        execute format('alter table public.%I enable row level security', target_table);

        execute format(
            'revoke all on public.%I from public, anon, authenticated',
            target_table
        );
        execute format(
            'grant select on public.%I to service_role',
            target_table
        );
    end loop;
end
$$;
