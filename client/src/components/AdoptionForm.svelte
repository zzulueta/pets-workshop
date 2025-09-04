<script lang="ts">
    import { onMount } from "svelte";
    
    interface Dog {
        id: number;
        name: string;
        breed: string;
        age: number;
        description: string;
        gender: string;
        status: 'AVAILABLE' | 'PENDING' | 'ADOPTED';
    }

    export let dog: Dog | undefined = undefined;
    export let dogId = 0;
    
    let loading = false;
    let error: string | null = null;
    let successMessage: string | null = null;
    let showForm = false;
    
    // Form data
    let applicantName = '';
    let email = '';
    let phone = '';
    let message = '';
    
    const resetForm = () => {
        applicantName = '';
        email = '';
        phone = '';
        message = '';
        error = null;
        successMessage = null;
    };
    
    const submitApplication = async () => {
        if (!dog) {
            error = "Dog information not available";
            return;
        }
        
        // Validate required fields
        if (!applicantName.trim()) {
            error = "Name is required";
            return;
        }
        
        if (!email.trim()) {
            error = "Email is required";
            return;
        }
        
        if (!email.includes('@')) {
            error = "Please enter a valid email address";
            return;
        }
        
        loading = true;
        error = null;
        
        try {
            const response = await fetch(`/api/dogs/${dog.id}/adopt`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    applicant_name: applicantName.trim(),
                    email: email.trim(),
                    phone: phone.trim() || null,
                    message: message.trim() || null
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                successMessage = "Your adoption application has been submitted successfully! We'll be in touch soon.";
                resetForm();
                showForm = false;
            } else {
                error = data.error || 'Failed to submit application';
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };
    
    const handleSubmit = (e: Event) => {
        e.preventDefault();
        submitApplication();
    };
</script>

{#if dog && dog.status === 'AVAILABLE'}
    <div class="mt-8">
        {#if !showForm && !successMessage}
            <div class="bg-slate-800/70 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
                <h3 class="text-xl font-semibold text-slate-100 mb-3">Interested in adopting {dog.name}?</h3>
                <p class="text-slate-300 mb-4">Submit an adoption application to let us know you're interested!</p>
                <button 
                    on:click={() => showForm = true}
                    class="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-all duration-300 font-medium flex items-center"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                    </svg>
                    Apply to Adopt {dog.name}
                </button>
            </div>
        {/if}
        
        {#if showForm}
            <div class="bg-slate-800/70 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
                <h3 class="text-xl font-semibold text-slate-100 mb-4">Adoption Application for {dog.name}</h3>
                
                <form on:submit={handleSubmit} class="space-y-4">
                    <div>
                        <label for="applicantName" class="block text-sm font-medium text-slate-300 mb-2">
                            Full Name *
                        </label>
                        <input
                            type="text"
                            id="applicantName"
                            bind:value={applicantName}
                            required
                            class="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Enter your full name"
                        />
                    </div>
                    
                    <div>
                        <label for="email" class="block text-sm font-medium text-slate-300 mb-2">
                            Email Address *
                        </label>
                        <input
                            type="email"
                            id="email"
                            bind:value={email}
                            required
                            class="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Enter your email address"
                        />
                    </div>
                    
                    <div>
                        <label for="phone" class="block text-sm font-medium text-slate-300 mb-2">
                            Phone Number (optional)
                        </label>
                        <input
                            type="tel"
                            id="phone"
                            bind:value={phone}
                            class="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Enter your phone number"
                        />
                    </div>
                    
                    <div>
                        <label for="message" class="block text-sm font-medium text-slate-300 mb-2">
                            Tell us about yourself (optional)
                        </label>
                        <textarea
                            id="message"
                            bind:value={message}
                            rows="4"
                            class="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Tell us about your experience with pets, living situation, why you want to adopt this dog, etc."
                        ></textarea>
                    </div>
                    
                    {#if error}
                        <div class="bg-red-500/20 border border-red-500/50 text-red-400 rounded-lg p-3">
                            {error}
                        </div>
                    {/if}
                    
                    <div class="flex space-x-3">
                        <button
                            type="submit"
                            disabled={loading}
                            class="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-800 text-white rounded-lg transition-all duration-300 font-medium disabled:cursor-not-allowed"
                        >
                            {loading ? 'Submitting...' : 'Submit Application'}
                        </button>
                        <button
                            type="button"
                            on:click={() => { showForm = false; resetForm(); }}
                            class="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded-lg transition-all duration-300"
                        >
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        {/if}
        
        {#if successMessage}
            <div class="bg-green-500/20 border border-green-500/50 text-green-400 rounded-xl p-6">
                <div class="flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                        <h4 class="font-semibold mb-1">Application Submitted!</h4>
                        <p class="text-green-300">{successMessage}</p>
                    </div>
                </div>
            </div>
        {/if}
    </div>
{:else if dog && dog.status === 'PENDING'}
    <div class="mt-8">
        <div class="bg-amber-500/20 border border-amber-500/50 text-amber-400 rounded-xl p-6">
            <div class="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                    <h4 class="font-semibold mb-1">Adoption Pending</h4>
                    <p class="text-amber-300">{dog.name} has a pending adoption application. Check back later to see if they become available again.</p>
                </div>
            </div>
        </div>
    </div>
{:else if dog && dog.status === 'ADOPTED'}
    <div class="mt-8">
        <div class="bg-red-500/20 border border-red-500/50 text-red-400 rounded-xl p-6">
            <div class="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
                <div>
                    <h4 class="font-semibold mb-1">Already Adopted</h4>
                    <p class="text-red-300">{dog.name} has already found their forever home! Check out our other available dogs.</p>
                </div>
            </div>
        </div>
    </div>
{/if}