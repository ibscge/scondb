<script>
    import { Heading, P } from "flowbite-svelte";
    import { page } from "$app/stores";
    import {
        Sidebar,
        SidebarGroup,
        SidebarItem,
        SidebarWrapper,
        Button,
        Navbar,
        NavBrand,
        NavLi,
        NavUl,
        NavHamburger,
    } from "flowbite-svelte";
    $: activeUrl = $page.url.pathname;
    let activeClass =
        "text-white font-semibold bg-green-700 md:bg-transparent md:text-green-700 md:dark:text-white dark:bg-green-600 md:dark:bg-transparent";
    let nonActiveClass =
        "text-gray-700 hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-green-700 dark:text-gray-400 md:dark:hover:text-white dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent";
</script>
<div class="w-full px-4 py-10">
    <div class="max-w-screen-xl min-w-[768px] mx-auto">
      <div class="w-full border-b border-gray-300 mb-4 pb-2">
        <Heading size="2xl" class="text-gray-800 font-bold text-left px-6">
          GENPOS
        </Heading>
      </div>
  
      <div class="mt-5 p-10 bg-green-100 rounded-lg">
        <P size="xl" weight="medium">Release Note</P>
        <div class="flex flex-row">
          <P size="medium" weight="medium" class="p-2">2024.10.15</P>
          <P class="p-2">Draft version publish</P>
        </div>
        <div class="flex flex-row">
          <P size="medium" weight="medium" class="p-2">2025.04.17</P>
          <P class="p-2">v1.0.0 First release</P>
        </div>
      </div>
  
      <div class="grid grid-cols-2 gap-4 mt-5">
        <div class="p-10 bg-green-100 rounded-lg">
          <P size="xl" weight="medium">Overview</P>
          <img src="/scondb_overview2.svg" alt="overview_Img" class="w-full h-auto mt-4" />
        </div>
        <div class="p-10 bg-green-100 rounded-lg">
          <P size="xl" weight="medium">Citation</P>
          <P class="mt-2">
            <a href="https://doi.org/10.1038/s12276-022-00891-0" target="_blank" rel="noopener noreferrer"
              class="text-black-600 hover:underline">
              Wu, SH.S., Lee, H., Szép-Bakonyi, R. et al. SCON—a Short Conditional intrON for conditional knockout with one-step zygote injection. Exp Mol Med 54, 2188–2199 (2022).
            </a>
          </P>
          <P class="mt-2">
            <a href="https://doi.org/10.1038/s41467-024-49382-y" target="_blank" rel="noopener noreferrer"
              class="text-black-600 hover:underline">
              Wu, SH.S., Kim, S., Lee, H. et al. Red2Flpe-SCON: a versatile, multicolor strategy for generating mosaic conditional knockout mice. Nat Commun 15, 4963 (2024).
            </a>
          </P>
        </div>
      </div>
    </div>
  </div>