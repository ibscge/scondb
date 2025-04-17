<script>
    import { page } from "$app/stores";
    import "../app.css";
    import {
        Sidebar,
        SidebarGroup,
        SidebarItem,
        SidebarWrapper,
    } from "flowbite-svelte";

    let activeClass =
        "flex items-center p-2 text-base font-normal text-primary-900 bg-primary-200 dark:bg-primary-700 rounded-lg dark:text-white hover:bg-primary-100 dark:hover:bg-gray-700";
    let nonActiveClass =
        "flex items-center p-2 text-base font-normal text-green-900 rounded-lg dark:text-white hover:bg-green-100 dark:hover:bg-green-700";
    let open;
    open = true;
</script>

<div class="relative h-full flex w-full">
    <button
        class="bg-green-500 rounded-r-full w-6 h-10 font-bold text-white absolute top-2"
        on:click={() => {
            open = !open;
        }}>{open ? "<" : ">"}</button
    >
    {#if open}<Sidebar class="flex w-21" {activeClass} {nonActiveClass}>
            <SidebarWrapper
                class="py-10 grow overflow-y-visible min-h-screen h-full w-21"
            >
                <SidebarGroup>
                    <SidebarItem
                        spanClass="px-3"
                        label="Home"
                        href="/"
                        active={$page.url.pathname === "/"}
                    ></SidebarItem>
                    <SidebarItem
                        spanClass="px-3"
                        label="Dataset"
                        href="/dataset"
                        active={$page.url.pathname === "/dataset"}
                    ></SidebarItem>
                    <SidebarItem
                        spanClass="px-3"
                        label="Analysis"
                        href="/analysis"
                        active={$page.url.pathname === "/analysis"}
                    ></SidebarItem>
                    <SidebarItem
                        spanClass="px-3"
                        label="Tutorial"
                        href="/tutorial"
                        active={$page.url.pathname === "/tutorial"}
                    ></SidebarItem>
                </SidebarGroup>
            </SidebarWrapper>
        </Sidebar>{/if}
    <slot class="w-11/12" />
</div>
