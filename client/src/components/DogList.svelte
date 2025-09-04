<script lang="ts">
    import { onMount } from "svelte";

    interface Dog {
        id: number;
        name: string;
        breed: string;
        status?: string; // e.g. AVAILABLE, ADOPTED, PENDING (from server)
    }

    export let dogs: Dog[] = [];
    let loading = true;
    let error: string | null = null;

    // UI state for filters
    let query = '';
    let breedFilter: string = 'ALL';
    // When true hide dogs that are adopted
    let hideAdopted = false;

    // derived list of breeds for the dropdown (updated when dogs change)
    $: breeds = Array.from(new Set(dogs.map(d => d.breed).filter(Boolean))).sort();

    const fetchDogs = async () => {
        loading = true;
        try {
            const response = await fetch('/api/dogs');
            if (response.ok) {
                dogs = await response.json();
            } else {
                error = `Failed to fetch data: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    onMount(() => {
        fetchDogs();
    });

    // Derived filtered list
    $: filteredDogs = dogs.filter((d) => {
        // search by name or breed
        const q = query.trim().toLowerCase();
        if (q) {
            const matches = (d.name || '').toLowerCase().includes(q) || (d.breed || '').toLowerCase().includes(q);
            if (!matches) return false;
        }

    // status handling: hide adopted when requested
    const status = (d.status || '').toUpperCase();
    if (hideAdopted && status === 'ADOPTED') return false;

    // breed filter
    if (breedFilter !== 'ALL' && (d.breed || '') !== breedFilter) return false;

        return true;
    });

    // small helper to display nicer status text
    function formatStatus(raw: string) {
        if (!raw) return '';
        const s = raw.toLowerCase();
        if (s === 'available' || s === 'AVAILABLE') return 'Available';
        if (s === 'adopted' || s === 'ADOPTED') return 'Adopted';
        if (s === 'pending' || s === 'PENDING') return 'Pending';
        // fall back to capitalized
        return raw.charAt(0).toUpperCase() + raw.slice(1).toLowerCase();
    }
</script>

<div>
    <h2 class="text-2xl font-medium mb-4 text-slate-100">Available Dogs</h2>

    <!-- Filters: search, dropdown, checkbox -->
    <div class="mb-6 flex flex-col sm:flex-row sm:items-center sm:gap-4">
        <div class="flex-1">
            <label for="dog-search" class="sr-only">Search dogs</label>
            <input
                id="dog-search"
                type="search"
                placeholder="Search by name or breed"
                bind:value={query}
                class="w-full bg-slate-700/60 text-slate-100 placeholder-slate-400 rounded-md p-3 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
        </div>

        <div class="mt-3 sm:mt-0">
            <label for="breed-select" class="sr-only">Filter by breed</label>
            <select
                id="breed-select"
                bind:value={breedFilter}
                class="bg-slate-700/60 text-slate-100 rounded-md p-2 border border-slate-600 focus:outline-none"
            >
                <option value="ALL">All breeds</option>
                {#each breeds as b}
                    <option value={b}>{b}</option>
                {/each}
            </select>
        </div>

        <div class="mt-3 sm:mt-0 flex items-center gap-2">
            <input id="hide-adopted" type="checkbox" bind:checked={hideAdopted} class="h-4 w-4 text-blue-500 bg-slate-700/60 border-slate-600 rounded" />
            <label for="hide-adopted" class="text-slate-300 text-sm">Hide adopted dogs</label>
        </div>
    </div>

    {#if loading}
        <!-- loading animation -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each Array(6) as _, i}
                <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50">
                    <div class="p-6">
                        <div class="animate-pulse">
                            <div class="h-6 bg-slate-700 rounded w-3/4 mb-3"></div>
                            <div class="h-4 bg-slate-700 rounded w-1/2 mb-4"></div>
                            <div class="h-4 bg-slate-700 rounded w-1/4 mt-6"></div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {:else if error}
        <!-- error display -->
        <div class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
            <p class="text-red-400">{error}</p>
        </div>
    {:else if filteredDogs.length === 0}
        <!-- no dogs found -->
        <div class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
            <p class="text-slate-300">No dogs match your filters.</p>
        </div>
    {:else}
        <!-- dog list -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each filteredDogs as dog (dog.id)}
                <a
                    href={`/dog/${dog.id}`}
                    class="group block bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50 hover:border-blue-500/50 hover:shadow-blue-500/10 hover:shadow-xl transition-all duration-300 hover:translate-y-[-6px]"
                >
                    <div class="p-6 relative">
                        <div class="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div class="relative z-10">
                            <h3 class="text-xl font-semibold text-slate-100 mb-2 group-hover:text-blue-400 transition-colors">{dog.name}</h3>
                            <p class="text-slate-400 mb-2">{dog.breed}</p>
                            {#if dog.status}
                                <p class="text-sm text-slate-400 mb-4">Status: <span class="font-medium text-slate-200">{formatStatus(dog.status)}</span></p>
                            {/if}
                            <div class="mt-4 text-sm text-blue-400 font-medium flex items-center">
                                <span>View details</span>
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1 transform transition-transform duration-300 group-hover:translate-x-2" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                                </svg>
                            </div>
                        </div>
                    </div>
                </a>
            {/each}
        </div>
    {/if}
</div>

<!-- helper merged into top <script> -->