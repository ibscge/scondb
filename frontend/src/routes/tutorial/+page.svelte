<script>
    import { Heading, NavLi, NavUl, P } from "flowbite-svelte";
    import { page } from "$app/stores";
    $: activeUrl = $page.url.pathname;
    let activeClass =
        "text-white font-semibold bg-green-700 md:bg-transparent md:text-green-700 md:dark:text-white dark:bg-green-600 md:dark:bg-transparent";
    let nonActiveClass =
        "text-gray-700 hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-green-700 dark:text-gray-400 md:dark:hover:text-white dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent";
</script>

<div class="p-10 w-full min-w-[768px] max-w-[1800px] mx-auto">
    <div class="w-full border-b border-gray-300 mb-4 pb-2">
        <Heading size="2xl" class="text-gray-800 font-bold text-left px-6">
          Tutorial
        </Heading>
      </div>

    <div class="mt-5 p-10 bg-green-50 rounded-lg">
        <P size="medium" weight="normal"
            >This page is designed to help you quickly and easily find the
            information you need. It provides a step-by-step guide on how to use
            the various features, ensuring an optimal user experience.
        </P>
    </div>
    <div class="grid grid-cols-2 gap-4">
        <img src="/scondb_fig3_tutorial.png" alt="overview_Img" class="m-3" />
        <div class="content-wrapper overflow-y-auto m-3" style="height: 1000px;">
            <Heading tag="h3" class="px-3 m-5">How to use?</Heading>
            <div class="p-3 m-5">
                <Heading tag="h4" class="text-lg font-semibold">STEP 1. Select MAGR or VDGN</Heading>
                <div class="mt-3 p-3 bg-green-50 rounded-lg">
                    <P size="medium" weight="medium" class="break-words">This option provides either MAGR((A/C)-A-G-(A/G)) or VDGN((A/G/C)-(A/T/G)-G-(A/T/G/C)) splice junction consensus sequence.</P>
                </div>
            </div>
            <div class="p-3 m-5">
                <Heading tag="h4" class="text-lg font-semibold">STEP 2. Search for the species you want to insert SCON and click</Heading>
                <div class="mt-3 p-3 bg-green-50 rounded-lg">
                    <P size="medium" weight="medium">You can also check and select the desired species from the Dataset menu.</P>
                </div>
            </div>
            <div class="p-3 m-5">
                <Heading tag="h4" class="text-lg font-semibold">STEP 3. Search for and select the gene you want to insert SCON</Heading>
                <div class="mt-3 p-3 bg-green-50 rounded-lg">
                    <P size="medium" weight="medium">When you enter the alphabet of the gene you want, the values ​​related to that alphabet will appear at the bottom of the input window, and you can click on the gene you want.</P>
                </div>
            </div>
            <div class="p-3 m-5">
                <Heading tag="h4" class="text-lg font-semibold">STEP 4. The exon ID contained in the corresponding gene is located in the leftmost column</Heading>
                <div class="mt-3 p-3 bg-green-50 rounded-lg">
                    <P size="medium" weight="medium">Exon ID provides ensembl ID information.</P>
                </div>
            </div>
            <div class="p-3 m-5">
                <Heading tag="h4" class="text-lg font-semibold">STEP 5. The transcript ID contained in the corresponding gene is located in the top row</Heading>
                <div class="mt-3 p-3 bg-green-50 rounded-lg">
                    <P size="medium" weight="medium">The transcript ID provides information about the ensemble ID, and clicking on it takes you to the ensemble site for more information.</P>
                </div>
            </div>
            <div class="p-3 m-5">
                <Heading tag="h4" class="text-lg font-semibold">STEP 6. Select the cell that matches the exon and transcript you want to insert SCON</Heading>
                <div class="mt-3 p-3 bg-green-50 rounded-lg">
                    <P size="medium" weight="medium">The number indicates the number of scon targetable sites.</P>
                </div>
            </div>
            <div class="p-3 m-5">
                <Heading tag="h4" class="text-lg font-semibold">STEP 7. Contains detailed information about the exons of the selected cell</Heading>
                <div class="mt-3 p-3 bg-green-50 rounded-lg">
                    <P size="medium" weight="medium">Clicking on each column will display detailed information about that column.</P>
                </div>
            </div>
        </div>
    </div>
</div>
