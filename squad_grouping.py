#!/usr/bin/env python3
"""Divide digital squads into groups of 6 following business rules."""

from dataclasses import dataclass

GROUP_SIZE = 6


@dataclass
class Member:
    name: str
    role: str
    squad: int
    squad_name: str
    is_blr: bool = False
    is_placeholder: bool = False
    is_shared: bool = False

    @property
    def groupable(self) -> bool:
        return not self.is_blr and not self.is_placeholder


SQUADS = [
    (1, "Shop Front Experience", [
        ("Arthur Mellor", "Product Manager"),
        ("Michael Leigh", "Product Designer"),
        ("Gayatri Sharma", "Iteration Manager", {"shared": True}),
        ("Simran Gill", "Business Analyst", {"shared": True}),
        ("Nicholas Kolotsos", "Engineer"),
        ("Zeeshan Mujtaba", "Engineer (C)"),
        ("Tajswini D", "Engineer (C) BLR", {"blr": True}),
        ("Ronny Rex", "Engineer (C) BLR", {"blr": True}),
        ("Kaustav Basu", "QA Engineer"),
        ("Raj Krishnan", "Tech Lead"),
        ("Alex Silva", "Engineer"),
    ]),
    (2, "Browse & Search Experience", [
        ("Alex Krstev (C)", "Product Manager"),
        ("Queenie Lo", "Product Designer"),
        ("Emre Rothzberg", "Lead Engineer"),
        ("Kawal Bhatti", "Engineer"),
        ("Jamie Nixon", "Engineer"),
        ("Dinithi De Silva", "Engineer (C) BLR", {"blr": True}),
        ("Monalisa Mohanty", "QA Engineer"),
    ]),
    (3, "Decisioning & Perso", [
        ("TBH", "Product Manager", {"placeholder": True}),
        ("Chetan Pundir", "Engineer"),
        ("Vim Herath", "Engineer"),
        ("Rahul Ronald", "QA Engineer"),
        ("TBH", "Senior Engineer", {"placeholder": True}),
        ("Julian Loo", "Business Analyst"),
        ("Jay Soeur", "Tech Lead"),
        ("Cheong Koo", "Iteration Manager"),
    ]),
    (4, "Product Experience", [
        ("Akshata Shanbhag", "Product Manager"),
        ("Venus Liu", "Product Designer"),
        ("Shane Mclachlan", "Iteration Manager (FTC)", {"shared": True}),
        ("Umara Wazeer", "Business Analyst", {"shared": True}),
        ("Siva Jonnalagadda", "Engineer"),
        ("Mikhail Prorekhin", "Engineer (C)"),
        ("Kiran Sahoo", "QA Engineer"),
        ("Jijesh Vannatham Veettil", "Lead Engineer"),
        ("Amir Ostadhossein", "Engineer"),
        ("Sujana Kunwar", "Engineer (C)"),
    ]),
    (5, "Product Data & Catalogue", [
        ("Khushboo Kumari", "Product Manager"),
        ("Shashank Biplav", "Engineer"),
    ]),
    (6, "Content Intelligence", []),
    (7, "Marketplace", [
        ("Divya Behl (C)", "Product Manager"),
        ("Praveen HR", "Engineer"),
        ("Alex Levshenko", "Engineer (C)"),
        ("Chris Wong", "Associate Engineer"),
        ("Fahad Bin Abid Janjua", "Tech Lead"),
        ("Nisarg Kapadia", "Iteration Manager", {"shared": True}),
    ]),
    (8, "Target App & Web Experience", [
        ("Rebecca Flarve", "Product Manager"),
        ("Bianca Higginson", "Product Designer"),
        ("Jules Williams", "Engineer"),
        ("San Kottuthala Mathew", "Business Analyst"),
        ("Farid Khan", "Tech Lead"),
        ("James Sun", "Senior Engineer"),
        ("Gouthami Korampalli", "Senior QA Engineer"),
    ]),
    (9, "Target Core (Hybris)", []),
    (10, "Digital Availability", [
        ("Tommy Nguyen", "Senior Engineer"),
        ("Shamith Amarawansa", "Engineer"),
        ("Aditya Shankar", "Business Analyst (C)"),
        ("Tu Huynh", "Associate Engineer"),
        ("Glenn Mai", "Tech Lead"),
    ]),
    (11, "Manhattan Inventory", [
        ("Arun Padmanabihan", "Lead Engineer"),
        ("Amrita Mohanty", "Product Manager"),
        ("Nidhin Janardhanan", "Iteration Manager", {"shared": True}),
    ]),
    (12, "Manhattan Availability", [
        ("Pratiksha Padmaprasad", "Senior Engineer (C)"),
        ("Sergey Markov", "Senior Engineer (C)"),
        ("Michael Au Dong", "Engineer (C)"),
        ("Jayani Jayatilleke", "Senior QA Engineer (C)"),
        ("Laura Larkin (C)", "Product Manager"),
    ]),
    (13, "Order Management", [
        ("Kunwar Karsh", "Product Manager"),
        ("Smita Patil", "Business Analyst"),
        ("Ankush Mahajan", "Senior QA Engineer (C)"),
        ("Monika Sharma", "Senior QA Engineer (C)"),
        ("Vibhas Kamal", "Iteration Manager (C)"),
        ("Binin Pottassery", "Senior Engineer"),
        ("Ashish Bhardwaj", "Senior Engineer"),
        ("Vineet Parvatikar", "QA Engineer"),
    ]),
    (14, "Fulfilment & Collection In-Store", [
        ("Cleo Zimakowski", "Product Manager"),
        ("Alex Patten", "Product Designer"),
        ("Gil Ferolino", "Tech Lead (C)"),
        ("Ljubisa Pakalavic", "Senior Engineer"),
        ("Sabreena Parambil", "Engineer (C)"),
        ("Tyron Gyde", "Product Designer (C)"),
        ("Fawad Amin", "Business Analyst (C)"),
    ]),
    (15, "Checkout Experience", [
        ("Joel Niran", "Product Manager"),
        ("Aidan Dao", "Product Designer"),
        ("Celina Lee", "Iteration Manager", {"shared": True}),
        ("Pratikkumar Patel", "Business Analyst", {"shared": True}),
        ("Chris Luo", "Tech Lead"),
        ("Ashvin Kumar Mohankumar", "Senior Engineer"),
        ("Jhansi Gidde", "Senior Engineer (C)"),
        ("Zack Kilmas", "Associate Engineer"),
        ("Jas Dhaliwal", "QA Engineer"),
        ("Atharva Telang", "Product Designer"),
    ]),
    (16, "Cart & Payments", [
        ("Sean Choi", "Senior Engineer (C)"),
        ("Lei Zhang", "Senior Engineer"),
        ("Guangyin Song", "Engineer"),
    ]),
    (17, "Omni & Post Purchase Experience", [
        ("Daniel Foulds", "Product Manager"),
        ("Prassannakumar Palani", "Product Designer"),
        ("Lakshmi Sursala", "Business Analyst", {"shared": True}),
        ("Peirong Xu", "Engineer"),
        ("Vikas Bawa", "Engineer"),
        ("Hiran Peiris", "Engineer (C)"),
        ("Katriona Wilder", "Associate Engineer"),
        ("Rui Xu", "Tech Lead"),
    ]),
    (18, "Customer Intelligence", [
        ("Krish Ragunathan", "Product Manager"),
        ("Jagath Murali", "Senior Engineer"),
        ("Neelima Gupta", "Senior Engineer"),
    ]),
    (19, "Loyalty & Engagement", [
        ("Valerie Li", "Product Manager"),
        ("Leili Mack", "Product Manager"),
        ("Rigel Maple", "Product Designer"),
        ("Swathi Jadhav", "Senior Engineer"),
        ("Oxana Alexandrova", "Senior Engineer"),
        ("Darcy Vreeken", "Engineer"),
        ("Lesley Laisina", "Engineer"),
        ("Michael Friedman", "Tech Lead"),
        ("Andrew Andrianopoulos", "Business Analyst / IM"),
    ]),
    (20, "Kmart App Ecosystem", [
        ("Photi Orfanidis", "Product Manager"),
        ("Janielyn Ascencio", "Product Designer"),
        ("Lija James", "QA Engineer"),
    ]),
    (21, "Design Systems & Experimentation", [
        ("Cherie Chan", "Design Technologist"),
        ("Will Xue", "Design Technologist (C)"),
        ("Oskar Simmons Carlsson", "Design Technologist"),
        ("Andrew Tralongo", "Product Designer"),
        ("Jordan Waje", "Senior Engineer"),
        ("Vivienne Dinh", "Product Designer"),
    ]),
    (22, "App Core", []),
    (23, "Web Core", [
        ("Antony Wei", "Engineer"),
        ("Brian Fung", "Engineer"),
        ("Vinodh Veeraraghavan", "Senior Engineer"),
        ("Wei Feng", "Lead Engineer"),
    ]),
    (24, "Care", [
        ("EJ Cho", "Product Designer"),
        ("Mason Conway", "Product Manager"),
    ]),
]


def build_members() -> list[Member]:
    members: list[Member] = []
    seen_shared: set[str] = set()

    for squad_num, squad_name, people in SQUADS:
        for entry in people:
            name, role = entry[0], entry[1]
            flags = entry[2] if len(entry) > 2 else {}
            is_blr = flags.get("blr", False) or " BLR" in role or role.endswith("BLR")
            is_placeholder = flags.get("placeholder", False) or name in ("TBH", "TBC")
            is_shared = flags.get("shared", False)

            if is_shared and name in seen_shared:
                continue
            if is_shared:
                seen_shared.add(name)

            members.append(
                Member(name, role, squad_num, squad_name, is_blr, is_placeholder, is_shared)
            )
    return members


def make_group(pool: list[Member], priority_squad: int | None = None) -> list[Member]:
    """Take 6 from pool, preferring members from priority_squad, then keeping carryover blocks."""
    if len(pool) < GROUP_SIZE:
        raise ValueError("Pool too small")

    group: list[Member] = []
    remaining = pool[:]

    if priority_squad is not None:
        for m in remaining:
            if m.squad == priority_squad and len(group) < GROUP_SIZE:
                group.append(m)
        for m in group:
            remaining.remove(m)

    for m in remaining:
        if len(group) < GROUP_SIZE:
            group.append(m)

    return group


def form_groups(members: list[Member]) -> list[dict]:
    groupable = [m for m in members if m.groupable]
    assigned: set[str] = set()
    groups: list[list[Member]] = []
    carryover: list[Member] = []

    squad_nums = sorted(set(m.squad for m in groupable))

    for idx, squad_num in enumerate(squad_nums):
        squad_members = [m for m in groupable if m.squad == squad_num and m.name not in assigned]

        # Batch squads 23+24 together (Web Core + Care = exactly 6)
        if squad_num == 23:
            squad_24 = [m for m in groupable if m.squad == 24 and m.name not in assigned]
            squad_members = squad_members + squad_24

        if squad_num == 24:
            continue

        # Large squads: form internal groups first
        if len(squad_members) >= 12:
            local = squad_members[:]
            while len(local) >= GROUP_SIZE:
                g = local[:GROUP_SIZE]
                local = local[GROUP_SIZE:]
                groups.append(g)
                for m in g:
                    assigned.add(m.name)
            carryover.extend(local)
            continue

        pool = carryover + squad_members
        carryover = []

        while len(pool) >= GROUP_SIZE:
            g = make_group(pool, priority_squad=squad_num)
            for m in g:
                pool.remove(m)
                assigned.add(m.name)
            groups.append(g)

        carryover = pool

    # Final pool
    pool = [m for m in carryover if m.name not in assigned]
    while len(pool) >= GROUP_SIZE:
        g = pool[:GROUP_SIZE]
        for m in g:
            pool.remove(m)
            assigned.add(m.name)
        groups.append(g)

    ungrouped = pool

    return [
        {
            "group_num": i + 1,
            "members": g,
            "squads": sorted(set(m.squad for m in g)),
            "squad_names": sorted({m.squad_name for m in g}),
        }
        for i, g in enumerate(groups)
    ], ungrouped


def markdown_for_miro(groups: list[dict], ungrouped: list[Member] | None = None) -> str:
    lines = [
        "# Digital Squad Groups of 6",
        "",
        "Rules applied:",
        "- BLR members excluded from grouping",
        "- Squad members kept together where possible",
        "- PM/PD and BA/IM may be in separate groups",
        "- Members borrowed from adjacent squads when needed to complete groups of 6",
        "",
    ]
    for g in groups:
        squad_label = " + ".join(f"Squad {s}" for s in g["squads"])
        lines.append(f"## Group {g['group_num']} ({squad_label})")
        lines.append("")
        for m in g["members"]:
            lines.append(f"- **{m.name}** — {m.role} _(Squad {m.squad}: {m.squad_name})_")
        lines.append("")
    if ungrouped:
        lines.append("## Not grouped (insufficient squad size)")
        lines.append("")
        for m in ungrouped:
            lines.append(f"- **{m.name}** — {m.role} _(Squad {m.squad}: {m.squad_name})_")
        lines.append("")
    return "\n".join(lines)


def table_rows(groups: list[dict]) -> list[dict]:
    rows = []
    for g in groups:
        for m in g["members"]:
            rows.append({
                "Group": f"Group {g['group_num']}",
                "Name": m.name,
                "Role": m.role,
                "Squad": f"Squad {m.squad}",
                "Squad Name": m.squad_name,
            })
    return rows


def main() -> None:
    members = build_members()
    groups, ungrouped = form_groups(members)
    groupable = [m for m in members if m.groupable]

    print(f"Groupable members: {len(groupable)}")
    print(f"Groups: {len(groups)}")
    print(f"Grouped: {sum(len(g['members']) for g in groups)}")
    if ungrouped:
        print(f"Ungrouped: {len(ungrouped)} ({', '.join(m.name for m in ungrouped)})")
    print()

    for g in groups:
        squads = ", ".join(f"S{s}" for s in g["squads"])
        print(f"Group {g['group_num']} ({squads}):")
        for m in g["members"]:
            print(f"  - {m.name} ({m.role}) [S{m.squad}]")
        print()

    with open("/workspace/squad_groups.md", "w") as f:
        f.write(markdown_for_miro(groups, ungrouped))

    import json
    with open("/workspace/squad_groups.json", "w") as f:
        json.dump(
            [
                {
                    "group_num": g["group_num"],
                    "squads": g["squads"],
                    "members": [
                        {"name": m.name, "role": m.role, "squad": m.squad, "squad_name": m.squad_name}
                        for m in g["members"]
                    ],
                }
                for g in groups
            ],
            f,
            indent=2,
        )


if __name__ == "__main__":
    main()
