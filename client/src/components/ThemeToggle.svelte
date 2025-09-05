<script lang="ts">
  import { onMount } from 'svelte';

  let theme: 'light' | 'dark' = 'dark';
  let mounted = false;

  // Initialize theme from localStorage or system preference
  onMount(() => {
    const storedTheme = localStorage.getItem('theme');
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    
    theme = storedTheme as 'light' | 'dark' || systemTheme;
    applyTheme(theme);
    mounted = true;

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem('theme')) {
        theme = e.matches ? 'dark' : 'light';
        applyTheme(theme);
      }
    };
    
    mediaQuery.addEventListener('change', handleChange);
    
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  });

  const applyTheme = (newTheme: 'light' | 'dark') => {
    const html = document.documentElement;
    if (newTheme === 'dark') {
      html.classList.add('dark');
    } else {
      html.classList.remove('dark');
    }
  };

  const toggleTheme = () => {
    theme = theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
    applyTheme(theme);
  };
</script>

<button
  on:click={toggleTheme}
  class="inline-flex items-center p-2 rounded-lg bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 dark:focus:ring-offset-slate-800"
  aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
  title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
>
  {#if mounted}
    {#if theme === 'light'}
      <!-- Moon icon for dark mode -->
      <svg 
        xmlns="http://www.w3.org/2000/svg" 
        class="h-5 w-5" 
        fill="none" 
        viewBox="0 0 24 24" 
        stroke="currentColor"
        aria-hidden="true"
      >
        <path 
          stroke-linecap="round" 
          stroke-linejoin="round" 
          stroke-width="2" 
          d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" 
        />
      </svg>
    {:else}
      <!-- Sun icon for light mode -->
      <svg 
        xmlns="http://www.w3.org/2000/svg" 
        class="h-5 w-5" 
        fill="none" 
        viewBox="0 0 24 24" 
        stroke="currentColor"
        aria-hidden="true"
      >
        <path 
          stroke-linecap="round" 
          stroke-linejoin="round" 
          stroke-width="2" 
          d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" 
        />
      </svg>
    {/if}
  {:else}
    <!-- Loading state placeholder -->
    <div class="h-5 w-5 animate-pulse bg-blue-300 dark:bg-blue-400 rounded"></div>
  {/if}
</button>