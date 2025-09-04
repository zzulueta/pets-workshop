<script lang="ts">
    import { onMount } from "svelte";
    
    interface Application {
        id: number;
        dog_id: number;
        dog_name: string;
        applicant_name: string;
        email: string;
        phone: string;
        message: string;
        application_status: string;
        submitted_at: string;
        updated_at: string;
    }

    let applications: Application[] = [];
    let loading = true;
    let error: string | null = null;
    
    const fetchApplications = async () => {
        loading = true;
        try {
            const response = await fetch('/api/applications');
            if (response.ok) {
                applications = await response.json();
            } else {
                error = `Failed to fetch applications: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };
    
    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };
    
    const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
            case 'submitted':
                return 'bg-blue-500/20 text-blue-400 border-blue-500/50';
            case 'under review':
                return 'bg-amber-500/20 text-amber-400 border-amber-500/50';
            case 'approved':
                return 'bg-green-500/20 text-green-400 border-green-500/50';
            case 'rejected':
                return 'bg-red-500/20 text-red-400 border-red-500/50';
            case 'completed':
                return 'bg-purple-500/20 text-purple-400 border-purple-500/50';
            default:
                return 'bg-slate-500/20 text-slate-400 border-slate-500/50';
        }
    };

    onMount(() => {
        fetchApplications();
    });
</script>

<div>
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-slate-100 mb-4">Adoption Applications</h1>
        <p class="text-slate-300">Review and manage adoption applications from potential adopters.</p>
    </div>
    
    {#if loading}
        <!-- Loading state -->
        <div class="space-y-4">
            {#each Array(3) as _, i}
                <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6 animate-pulse">
                    <div class="flex justify-between items-start mb-4">
                        <div class="space-y-2">
                            <div class="h-6 bg-slate-700 rounded w-48"></div>
                            <div class="h-4 bg-slate-700 rounded w-32"></div>
                        </div>
                        <div class="h-6 bg-slate-700 rounded w-20"></div>
                    </div>
                    <div class="space-y-2">
                        <div class="h-4 bg-slate-700 rounded w-full"></div>
                        <div class="h-4 bg-slate-700 rounded w-3/4"></div>
                    </div>
                </div>
            {/each}
        </div>
    {:else if error}
        <!-- Error state -->
        <div class="bg-red-500/20 border border-red-500/50 text-red-400 rounded-xl p-6">
            <div class="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                    <h4 class="font-semibold mb-1">Error Loading Applications</h4>
                    <p>{error}</p>
                </div>
            </div>
        </div>
    {:else if applications.length === 0}
        <!-- Empty state -->
        <div class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-slate-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 class="text-xl font-semibold text-slate-100 mb-2">No Applications Yet</h3>
            <p class="text-slate-400">When people submit adoption applications, they'll appear here.</p>
        </div>
    {:else}
        <!-- Applications list -->
        <div class="space-y-6">
            {#each applications as app (app.id)}
                <div class="bg-slate-800/70 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <h3 class="text-xl font-semibold text-slate-100 mb-1">
                                {app.applicant_name}
                            </h3>
                            <p class="text-slate-300 mb-2">
                                Interested in adopting: 
                                <a href="/dog/{app.dog_id}" class="text-blue-400 hover:text-blue-300 underline">
                                    {app.dog_name}
                                </a>
                            </p>
                            <p class="text-sm text-slate-400">
                                Submitted: {formatDate(app.submitted_at)}
                            </p>
                        </div>
                        <span class="px-3 py-1 text-sm rounded-full border {getStatusColor(app.application_status)}">
                            {app.application_status}
                        </span>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                            <h4 class="text-sm font-medium text-slate-300 mb-1">Contact Information</h4>
                            <p class="text-slate-400">Email: {app.email}</p>
                            {#if app.phone}
                                <p class="text-slate-400">Phone: {app.phone}</p>
                            {/if}
                        </div>
                        <div>
                            <h4 class="text-sm font-medium text-slate-300 mb-1">Application ID</h4>
                            <p class="text-slate-400">#{app.id}</p>
                        </div>
                    </div>
                    
                    {#if app.message}
                        <div class="mb-4">
                            <h4 class="text-sm font-medium text-slate-300 mb-2">Message from Applicant</h4>
                            <div class="bg-slate-700/30 rounded-lg p-3 border border-slate-600">
                                <p class="text-slate-300 italic">"{app.message}"</p>
                            </div>
                        </div>
                    {/if}
                    
                    <div class="flex flex-wrap gap-2">
                        <a 
                            href="/dog/{app.dog_id}" 
                            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all duration-300 text-sm"
                        >
                            View Dog Profile
                        </a>
                        <a 
                            href="mailto:{app.email}" 
                            class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-all duration-300 text-sm"
                        >
                            Contact Applicant
                        </a>
                        {#if app.phone}
                            <a 
                                href="tel:{app.phone}" 
                                class="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded-lg transition-all duration-300 text-sm"
                            >
                                Call
                            </a>
                        {/if}
                    </div>
                </div>
            {/each}
        </div>
        
        <div class="mt-8 text-center">
            <button 
                on:click={fetchApplications}
                class="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded-lg transition-all duration-300"
            >
                Refresh Applications
            </button>
        </div>
    {/if}
</div>