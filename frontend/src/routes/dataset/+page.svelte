<script>
    import { onMount, setContext } from "svelte";
    import { load } from "../../lib/fetch";
    import { page } from "$app/stores";
    import {
        Table,
        TableBody,
        TableBodyCell,
        TableBodyRow,
        TableHead,
        TableHeadCell,
        Heading,
        GradientButton,
        Button,
    } from "flowbite-svelte";
    import { selectedSpecies } from "../../lib/stores";

    let dataset = [];
    let mounted = false;

    function goToAnalysis(species) {
        selectedSpecies.set(species);
        console.log(species);
    }

    onMount(async () => {
        const rtn = await load("meta/dataset");
        dataset = rtn;
        mounted = true;
        console.log(rtn);
    });
</script>

<div class="p-3">
    <Heading class="p-5">Available Dataset</Heading>
    {#if mounted}
        <Table>
            <TableHead>
                <TableHeadCell>Species</TableHeadCell>
                <TableHeadCell>Ensemble revision</TableHeadCell>
                <TableHeadCell>Dataset</TableHeadCell>
                <TableHeadCell></TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#each dataset as s, i}<TableBodyRow>
                        <TableBodyCell>{s.species}</TableBodyCell>
                        <TableBodyCell>{s.ensemble_rev}</TableBodyCell>
                        <TableBodyCell>{s.name}</TableBodyCell>
                        <TableBodyCell
                            ><GradientButton
                                outline
                                color="tealToLime"
                                href="/analysis"
                                active={$page.url.pathname === "/analysis"}
                                on:click={() => goToAnalysis(s.species)}
                                >Go to Analysis</GradientButton
                            ></TableBodyCell
                        >
                    </TableBodyRow>{/each}
            </TableBody>
        </Table>
    {/if}
</div>
