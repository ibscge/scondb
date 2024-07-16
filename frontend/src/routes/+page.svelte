<script>
    import { Heading, P } from "flowbite-svelte";
    import { page } from "$app/stores";
    import {
        Sidebar,
        SidebarGroup,
        SidebarItem,
        SidebarWrapper,
        Button,
    } from "flowbite-svelte";
    let activeClass =
        "flex items-center p-2 text-base font-normal text-primary-900 bg-primary-200 dark:bg-primary-700 rounded-lg dark:text-white hover:bg-primary-100 dark:hover:bg-gray-700";
    let nonActiveClass =
        "flex items-center p-2 text-base font-normal text-green-900 rounded-lg dark:text-white hover:bg-green-100 dark:hover:bg-green-700";
</script>

<div class="p-10 w-11/12">
    <Heading>SCON analysis</Heading>
    <P class="py-3">18.2.0</P>
</div>
