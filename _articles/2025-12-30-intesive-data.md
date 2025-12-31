---
layout: post
title: "Data Intensive Systems visual mnemonics"
author: Slobodan Ninkov
---

{% assign imgs = "part0_overall_mnemoic.jpg,
                  part1_reliable_scalable_maintainable_applications.png,
                  part2_data_models_and_query.jpg,
                  part3_storage_and_retrieval.jpg,
                  part4_encoding_and_evolution.jpg,
                  part5_replication.jpg,
                  part6_partitioning.jpg,
                  part7_transactions.jpg,
                  part8_troublewithdistributions.jpg,
                  part9_consistency_and_consensus.jpg,
                  part10_batch_processing.jpg,
                  part11_stream_processing.jpg,
                  part12_future_of_data_systems.jpg,
                  part13_data_lakehouse_architecture_layers.jpg" | split: "," %}

{% for img in imgs %}
  <figure class="full-img">
    <img src="{{ '/assets/img/dis/' | append: img | relative_url }}" alt="{{ img }}">
  </figure>
{% endfor %}
