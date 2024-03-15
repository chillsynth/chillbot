from discord.ext import commands
from discord import app_commands
import os
import time
import discord
import motor.motor_asyncio
import asyncio
import logging
from datetime import datetime


#   TODO AFTER LIVE:
#       Slot command to manually change amount of slots
#       Add -> indicator on manually moved queue slots
#       Pre-waiting lobby thing - have to click submit manually when opened
# import random

class FeedbackQueueView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # DB Setup
        self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("DEV_MONGO_URI"))
        self.db = self.client["_events"]

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)

    async def search_db(self, document_name: str, document_key: dict):
        db_result = None
        async for result in getattr(self.db, document_name).find(document_key):
            db_result = result

        return db_result

    async def enable_buttons(self, channel_id: discord.Thread, message_id: int):
        self.add_queue_submission.disabled = False
        self.add_queue_submission.style = discord.ButtonStyle.success
        self.edit_queue_submission.disabled = False
        self.edit_queue_submission.style = discord.ButtonStyle.blurple

        original_message_id: discord.Message = await channel_id.fetch_message(message_id)

        await original_message_id.edit(view=self)  # Update current button view

    # Sort through current Feedback Queue™ and return result
    async def sort_feedback_queue(self, interaction: discord.Interaction, display: bool):
        existing_queue = []
        async for document in self.db.feedback_queue.find({}):
            self.logger.debug(f"Events.cog: {document}")
            existing_queue.append(document)

        self.logger.debug(f"Events.cog: existing_queue: {existing_queue}")

        nitro_queue = []
        normal_queue = []
        insert_queue = []
        for member in existing_queue:
            if "queue_slot" in member:  # Check if member needs a specific queue slot
                insert_queue.append(member)
            else:
                if member["has_priority"]:  # Separate nitro boosters from non-boosters
                    nitro_queue.append(member)
                elif not member["has_priority"]:
                    normal_queue.append(member)
                else:
                    print("ERROR HERE FOR SOME REASON")
                    self.logger.warning(f"Events.cog: Error splitting users into queues in sort_feedback_queue()")

        def time_check(elem):
            return elem["time_added"]

        nitro_queue.sort(key=time_check, reverse=True)
        normal_queue.sort(key=time_check, reverse=True)
        pre_merged_queue = nitro_queue + normal_queue  # Merge both queues together
        post_merged_queue: list = pre_merged_queue

        for member in insert_queue:  # Insert members into a specific slot in the queue
            post_merged_queue.insert(member["queue_slot"], member)

        print(f"Nitro Queue: {nitro_queue}")
        print(f"Normal Queue: {normal_queue}")
        print(f"Merged Queue [pre-insert]: {pre_merged_queue}")
        print(f"Merged Queue [post-insert]: {post_merged_queue}")

        final_queue = "# Feedback Queue™\n"

        for user in post_merged_queue:
            if user["track_done"]:  # Already played their track
                final_queue += f"## <:XanderGlue_GREEN:1124041375093116998><@{user['track_user_ID']}>\n"
            elif user["has_priority"]:  # Supporter
                final_queue += f"## <:XanderGlue_NITRO:1124041876002066544><@{user['track_user_ID']}>\n"
            elif not user["has_priority"]:  # Not supporter
                final_queue += f"## <:XanderGlueBW:1123631048815808532><@{user['track_user_ID']}>\n"
            else:
                print("Something has gone terribly wrong")
                self.logger.warning(f"Events.cog: Unknown error appending user to final queue in sort_feedback_queue()")

        # Search DB record for original thread message
        key = {"submission_locator": "here i am"}
        response_msg = None
        async for result in self.db.information.find(key):
            response_msg = result

        response_channel = interaction.client.get_channel(response_msg["channel_ID"])
        response_msg = await response_channel.fetch_message(response_msg["message_ID"])

        if display:
            await response_msg.edit(content=f"{final_queue}")
        else:
            return post_merged_queue

    @discord.ui.button(label="Add To Queue",
                       style=discord.ButtonStyle.grey,
                       custom_id="add_queue",
                       emoji="<:DynamicBladeBW:1122666182546296967>",
                       disabled=True)
    async def add_queue_submission(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True  # Disable all buttons until complete
        self.edit_queue_submission.disabled = True

        await interaction.response.defer()

        # Search DB record for original thread message
        key = {"thread_ID": interaction.channel.id}
        search_result = None
        async for result in self.db.current_submissions.find(key):
            search_result = result

        original_message_id = await interaction.channel.fetch_message(search_result["thread_message_ID"])

        await original_message_id.edit(view=self)  # Update current button view

        allowed_event_role = discord.utils.get(interaction.guild.roles, name="Event Host")

        if allowed_event_role in interaction.user.roles:  # ALLOWED TO PRESS THE BUTTON - Proceed with adding to queue
            if button.custom_id == "add_queue":  # ADD TO QUEUE!
                button.label = "Remove From Queue"
                button.style = discord.ButtonStyle.danger
                button.custom_id = "remove_queue"
                button.emoji = "<:TangyCapacitorBW:1123631046508937379>"
                button.disabled = False

                self.edit_queue_submission.disabled = True
                await original_message_id.edit(view=self)  # Update current button view

                # Search DB record for submission data
                key = {"thread_ID": interaction.channel.id}
                search_result = None
                async for result in self.db.current_submissions.find(key):
                    search_result = result
                    print(result)

                existing_queue = []
                async for document in self.db.feedback_queue.find({}):
                    print(document)
                    existing_queue.append(document)

                if len(existing_queue) == 0:  # If queue is empty, then 1st entry
                    print("EMPTY QUEUE!")
                    # Submit new DB record with submission data
                    await self.db.feedback_queue.insert_one(
                        {
                            "track_user": str(search_result["thread_title"][:-13]),
                            "has_priority": bool(search_result["has_priority"]),
                            "time_added": int(search_result["time_added"]),
                            "track_URL": str(search_result["submission_URL"]),
                            "track_user_ID": int(search_result["user_ID"]),
                            "track_thread_ID": int(interaction.channel.id),
                            "track_done": False
                        }
                    )

                    # print(f"Added for {interaction.channel.name}")  # FOR DEBUG
                    self.logger.info(f"Events.cog: Added for {interaction.channel.name}")

                    # https://discohook.org/?data=eyJtZXNzYWdlcyI6W3siZGF0YSI6eyJjb250ZW50IjpudWxsLCJlbWJlZHMiOlt7ImNvbG9yIjoxNjc0NDgzMCwiZmllbGRzIjpbeyJuYW1lIjoiQ1VSUkVOVExZIFBMQVlJTkciLCJ2YWx1ZSI6IlRlc3QgVHJhY2sgLSBIdXJsZXliaXJkIiwiaW5saW5lIjp0cnVlfSx7Im5hbWUiOiJTdWJtaXR0ZWQgQnkiLCJ2YWx1ZSI6IlVzZXJuYW1lIzAwMDEifV0sImZvb3RlciI6eyJ0ZXh0IjoiTGFzdCBVcGRhdGVkIn0sInRpbWVzdGFtcCI6IjIwMjMtMDEtMzBUMjM6MDE6MDAuMDAwWiIsInRodW1ibmFpbCI6eyJ1cmwiOiJodHRwczovL2Nkbi5kaXNjb3JkYXBwLmNvbS9hdmF0YXJzLzM2MDg4MjkwMzkxMzIwMTY3NS9hX2I1YTYzMGVmYmJhMmNhMTY0NjRkMTRjYTQ4MmRjNWE3LmdpZj9zaXplPTEwMjQifX0seyJ0aXRsZSI6IlVQIE5FWFQiLCJjb2xvciI6MzQ5NzA4MywiZmllbGRzIjpbeyJuYW1lIjoiPiAxIiwidmFsdWUiOiJ0cmFjayBuYW1lIC0gYXJ0aXN0IG5hbWUiLCJpbmxpbmUiOnRydWV9LHsibmFtZSI6Ij4gMiIsInZhbHVlIjoidHJhY2sgbmFtZSAtIGFydGlzdCBuYW1lIiwiaW5saW5lIjp0cnVlfSx7Im5hbWUiOiI-IDMiLCJ2YWx1ZSI6InRyYWNrIG5hbWUgLSBhcnRpc3QgbmFtZSIsImlubGluZSI6dHJ1ZX0seyJuYW1lIjoiPiA0IiwidmFsdWUiOiJ0cmFjayBuYW1lIC0gYXJ0aXN0IG5hbWUiLCJpbmxpbmUiOnRydWV9LHsibmFtZSI6Ij4gNSIsInZhbHVlIjoidHJhY2sgbmFtZSAtIGFydGlzdCBuYW1lIiwiaW5saW5lIjp0cnVlfSx7Im5hbWUiOiI-IDYiLCJ2YWx1ZSI6InRyYWNrIG5hbWUgLSBhcnRpc3QgbmFtZSIsImlubGluZSI6dHJ1ZX0seyJuYW1lIjoiPiA3IiwidmFsdWUiOiJ0cmFjayBuYW1lIC0gYXJ0aXN0IG5hbWUiLCJpbmxpbmUiOnRydWV9LHsibmFtZSI6Ij4gOCIsInZhbHVlIjoidHJhY2sgbmFtZSAtIGFydGlzdCBuYW1lIiwiaW5saW5lIjp0cnVlfSx7Im5hbWUiOiI-IDkiLCJ2YWx1ZSI6InRyYWNrIG5hbWUgLSBhcnRpc3QgbmFtZSIsImlubGluZSI6dHJ1ZX1dLCJmb290ZXIiOnsidGV4dCI6Ikxhc3QgVXBkYXRlZCJ9LCJ0aW1lc3RhbXAiOiIyMDIzLTAxLTMwVDIzOjAxOjAwLjAwMFoifV0sInVzZXJuYW1lIjoiRmVlZGJhY2sgU3RyZWFt4oSiIFF1ZXVlIiwiYXR0YWNobWVudHMiOltdfX1dfQ

                    await interaction.channel.send(
                        content=f"**Added** <#{interaction.channel.id}> to the Feedback Stream™ Queue!")

                else:  # Queue isn't empty - add track then sort queue
                    # Submit new DB record with submission data
                    await self.db.feedback_queue.insert_one(
                        {
                            "track_user": str(search_result["thread_title"][:-13]),
                            "has_priority": bool(search_result["has_priority"]),
                            "time_added": int(search_result["time_added"]),
                            "track_URL": str(search_result["submission_URL"]),
                            "track_user_ID": int(search_result["user_ID"]),
                            "track_thread_ID": int(interaction.channel.id),
                            "track_done": False
                        }
                    )

                    # print(f"Added for {interaction.channel.name}")  # FOR DEBUG

                    # https://discohook.org/?data=eyJtZXNzYWdlcyI6W3siZGF0YSI6eyJjb250ZW50IjpudWxsLCJlbWJlZHMiOlt7ImNvbG9yIjoxNjc0NDgzMCwiZmllbGRzIjpbeyJuYW1lIjoiQ1VSUkVOVExZIFBMQVlJTkciLCJ2YWx1ZSI6IlRlc3QgVHJhY2sgLSBIdXJsZXliaXJkIiwiaW5saW5lIjp0cnVlfSx7Im5hbWUiOiJTdWJtaXR0ZWQgQnkiLCJ2YWx1ZSI6IlVzZXJuYW1lIzAwMDEifV0sImZvb3RlciI6eyJ0ZXh0IjoiTGFzdCBVcGRhdGVkIn0sInRpbWVzdGFtcCI6IjIwMjMtMDEtMzBUMjM6MDE6MDAuMDAwWiIsInRodW1ibmFpbCI6eyJ1cmwiOiJodHRwczovL2Nkbi5kaXNjb3JkYXBwLmNvbS9hdmF0YXJzLzM2MDg4MjkwMzkxMzIwMTY3NS9hX2I1YTYzMGVmYmJhMmNhMTY0NjRkMTRjYTQ4MmRjNWE3LmdpZj9zaXplPTEwMjQifX0seyJ0aXRsZSI6IlVQIE5FWFQiLCJjb2xvciI6MzQ5NzA4MywiZmllbGRzIjpbeyJuYW1lIjoiPiAxIiwidmFsdWUiOiJ0cmFjayBuYW1lIC0gYXJ0aXN0IG5hbWUiLCJpbmxpbmUiOnRydWV9LHsibmFtZSI6Ij4gMiIsInZhbHVlIjoidHJhY2sgbmFtZSAtIGFydGlzdCBuYW1lIiwiaW5saW5lIjp0cnVlfSx7Im5hbWUiOiI-IDMiLCJ2YWx1ZSI6InRyYWNrIG5hbWUgLSBhcnRpc3QgbmFtZSIsImlubGluZSI6dHJ1ZX0seyJuYW1lIjoiPiA0IiwidmFsdWUiOiJ0cmFjayBuYW1lIC0gYXJ0aXN0IG5hbWUiLCJpbmxpbmUiOnRydWV9LHsibmFtZSI6Ij4gNSIsInZhbHVlIjoidHJhY2sgbmFtZSAtIGFydGlzdCBuYW1lIiwiaW5saW5lIjp0cnVlfSx7Im5hbWUiOiI-IDYiLCJ2YWx1ZSI6InRyYWNrIG5hbWUgLSBhcnRpc3QgbmFtZSIsImlubGluZSI6dHJ1ZX0seyJuYW1lIjoiPiA3IiwidmFsdWUiOiJ0cmFjayBuYW1lIC0gYXJ0aXN0IG5hbWUiLCJpbmxpbmUiOnRydWV9LHsibmFtZSI6Ij4gOCIsInZhbHVlIjoidHJhY2sgbmFtZSAtIGFydGlzdCBuYW1lIiwiaW5saW5lIjp0cnVlfSx7Im5hbWUiOiI-IDkiLCJ2YWx1ZSI6InRyYWNrIG5hbWUgLSBhcnRpc3QgbmFtZSIsImlubGluZSI6dHJ1ZX1dLCJmb290ZXIiOnsidGV4dCI6Ikxhc3QgVXBkYXRlZCJ9LCJ0aW1lc3RhbXAiOiIyMDIzLTAxLTMwVDIzOjAxOjAwLjAwMFoifV0sInVzZXJuYW1lIjoiRmVlZGJhY2sgU3RyZWFt4oSiIFF1ZXVlIiwiYXR0YWNobWVudHMiOltdfX1dfQ

                    await interaction.channel.send(
                        content=f"**Added** <#{interaction.channel.id}> to the Feedback Stream™ Queue!")
                    self.logger.info(f"Events.cog: Added for {interaction.channel.name}")

            # REMOVE TRACK FROM QUEUE
            elif button.custom_id == "remove_queue":
                button.label = "Add To Queue"
                button.style = discord.ButtonStyle.success
                button.custom_id = "add_queue"
                button.emoji = "<:DynamicBladeBW:1122666182546296967>"
                button.disabled = False

                self.edit_queue_submission.disabled = False  # Re-enable edits for submission
                await original_message_id.edit(view=self)  # Update current button view

                print("Permission check passed!")

                # Locate submission's ObjectID and delete record in DB
                key = {"track_thread_ID": interaction.channel.id}

                # Search and delete DB record
                async for result in self.db.feedback_queue.find(key):
                    delete_key = {"_id": result["_id"]}
                    await self.db.feedback_queue.delete_one(delete_key)
                    print(
                        f"Deleted record for {interaction.channel.name} ObjectID:{result['_id']}")
                    self.logger.info(f"Events.cog: Deleted record for {interaction.channel.name} in DB")

                await interaction.channel.send(
                    content=f"**Removed** <#{interaction.channel.id}> from the Feedback Stream™ Queue.")

        else:  # NOT ALLOWED TO PRESS THE BUTTON - IGNORE
            button.disabled = False  # Re-enable buttons
            self.edit_queue_submission.disabled = False
            await original_message_id.edit(view=self)  # Update current button view

            await interaction.followup.send(
                content=f"### <@{interaction.user.id}>, __only__ Event Hosts can add tracks to the Feedback Queue™",
                ephemeral=True)

        # Update the current queue
        await self.sort_feedback_queue(interaction, True)

    @discord.ui.button(label="Edit Submission",
                       style=discord.ButtonStyle.grey,
                       custom_id="edit_submission_button",
                       emoji="<:ConnectedWaterBW:1123631044931891260>",
                       disabled=True)
    async def edit_queue_submission(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        self.add_queue_submission.disabled = True
        await interaction.response.defer()

        # Search DB record for original thread message
        key = {"thread_ID": interaction.channel.id}
        search_result = None
        async for result in self.db.current_submissions.find(key):
            search_result = result

        original_message_id = await interaction.channel.fetch_message(search_result["thread_message_ID"])
        await original_message_id.edit(view=self)

        # Buttons are now disabled - continue
        temp_edit_msg = await interaction.channel.send(content="## Please put the updated link/file below:")

        def edit_check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        msg = await interaction.client.wait_for("message", check=edit_check)
        print(str(msg))

        edited_url = "If you're reading this, something broke :)"
        if msg.content:  # Message is a text URL - store as is
            edited_url = msg.content
            print(str(msg.content))
        elif msg.attachments:  # Message contains a file - store file URL for playing
            edited_url = msg.attachments[0].url
            print(str(msg.attachments[0].url))

        submission_updated_value = {
            "$set": {
                "user_ID": int(interaction.user.id),
                "thread_ID": int(interaction.channel.id),
                "submission_URL": str(edited_url),  # Update with new URL
                "has_priority": search_result["has_priority"],
                "time_added": int(datetime.now().strftime('%H%M%S')),
                "thread_message_ID": search_result["thread_message_ID"],
                "thread_title": search_result["thread_title"]
            }
        }

        db_filter = {"user_ID": interaction.user.id}  # Filter by userID
        await self.db.current_submissions.update_one(db_filter, submission_updated_value)

        await temp_edit_msg.delete()  # Submission edited - delete old message

        await interaction.followup.send(
            content=f"Changed submission to {edited_url}!",
            ephemeral=True
        )
        button.disabled = False
        self.add_queue_submission.disabled = False
        await original_message_id.edit(view=self)

    @discord.ui.button(label="Cancel Submission",
                       style=discord.ButtonStyle.red,
                       custom_id="delete_submission_button",
                       emoji="<:TangyCapacitorBW:1123631046508937379>",
                       disabled=False)
    async def revoke_queue_submission(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.edit_queue_submission.disabled = True
        self.add_queue_submission.disabled = True
        await interaction.response.defer()

        # Buttons are now disabled - continue
        # Check if slot taken
        # Search DB record for original thread message
        key = {"thread_ID": interaction.channel.id}
        search_result = None
        async for result in self.db.current_submissions.find(key):
            search_result = result

        if search_result is None:  # No submission sent - slot is still free
            pass
        else:
            # Delete feedback_queue / submission_queue DB record and update feedback_queue if needed
            # Find and delete submission queue DB record
            db_filter = {"thread_ID": interaction.channel.id}  # Filter by thread ID
            await self.db.current_submissions.delete_one(db_filter)

            db_filter = {"track_thread_ID": interaction.channel.id}  # Filter by thread ID
            await self.db.feedback_queue.delete_one(db_filter)

            # Update the current queue
            await self.sort_feedback_queue(interaction, True)

            slots_data = await self.search_db("information",
                                              {"submission_locator": "here i am"})

            # Submission slot freed - increment slot counter
            await self.db.information.update_one(
                {"slots": slots_data["slots"]},
                {"$inc": {"slots": 1}}
            )

            await SubmitView(interaction).refresh_button_state(interaction, False)

        # Clean up and freeze channel for deletion
        button.disabled = True
        await interaction.channel.edit(name="X")
        current_unix = int(time.time() + 1801)

        await interaction.followup.send(
            content=f"## {interaction.user.mention} revoked submission from the event! \n\n"
                    f"### <:Discord_Timeout:1140060025876922482> This message will expire <t:{current_unix}:R>"
        )

        await asyncio.sleep(1800)
        await interaction.channel.delete()


class SubmitView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=None)

        # DB Setup
        self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("DEV_MONGO_URI"))
        self.db = self.client["_events"]

    async def search_db(self, document_name: str, document_key: dict):
        db_result = None
        async for result in getattr(self.db, document_name).find(document_key):
            db_result = result

        return db_result

    async def refresh_button_state(self, interaction: discord.Interaction, value_return: bool):
        search_result = await SubmitView.search_db(self, "information",
                                                   {"submission_locator": "here i am"})

        if search_result["slots"] <= 0:
            self.create_submission_button.disabled = True
        else:
            self.create_submission_button.disabled = False

        self.slot_button.label = f"Slots remaining: {search_result['slots']}"

        original_channel = interaction.client.get_channel(search_result["channel_ID"])
        original_message_id: discord.Message = await original_channel.fetch_message(search_result["message_ID"])

        await original_message_id.edit(view=self)  # Update current button view

        if value_return:
            return {"channel_ID": search_result["channel_ID"],
                    "message_ID": search_result["message_ID"],
                    "slots": search_result["slots"]}

    @discord.ui.button(label=f"Create Submission",
                       style=discord.ButtonStyle.success,
                       custom_id="submission_button",
                       emoji="<:DynamicBladeBW:1122666182546296967>")
    async def create_submission_button(self, interaction: discord.Interaction, button: discord.Button):
        """
        INIT:
        Check if available slots before making a new thread
        IF slots are not available:
            Button should be disabled until slots become available
        ELSE:
            Create a new thread and create submission DB record
        """
        await interaction.response.defer()

        # TODO: This need to be made redundant and update before someone wants to create a submission
        refresh_data = await self.refresh_button_state(interaction, True)

        # Check if slots available then proceed, else refresh, close button and await freed slot

        if refresh_data["slots"] <= 0:
            await interaction.followup.send(content=f"Sorry! All slots have been taken.",
                                            ephemeral=True)
        else:
            # SLOTS STILL REMAIN - PROCEED

            thread_name = f"{interaction.user.global_name}-{str(datetime.now().strftime('%H%M%S%d%m%y'))}"
            new_thread = await interaction.channel.create_thread(name=thread_name,
                                                                 invitable=False,
                                                                 type=discord.ChannelType.private_thread)

            thread_msg = await new_thread.send(
                f"||<@{interaction.user.id}><@&{os.getenv('DEV_EVENT_ROLE_ID')}>||\n"
                f"### IMPORTANT : Private SoundCloud links must have **`s-`** in the URL like this:\n"
                f"> **soundcloud.com/hurleybirdjr/example-track/`s-`1nqsSuAAk79**\n## ~\n"
                f"## Please upload your `.mp3` / `.wav` / `.flac` file below\n### OR\n"
                f"## submit your SoundCloud __Private__ link:",

                view=FeedbackQueueView())

            await interaction.followup.send(content=f"New thread created! <#{new_thread.id}>",
                                            ephemeral=True)

            def edit_check(m):
                return m.author == interaction.user and m.channel == new_thread

            msg = await interaction.client.wait_for("message", check=edit_check)
            print(str(msg))

            edited_url = "If you're reading this, something broke :)"
            if msg.content:  # Message is a text URL - store as is
                edited_url = msg.content
                print(str(msg.content))
            elif msg.attachments:  # Message contains a file - store file URL for playing
                edited_url = msg.attachments[0].url
                print(str(msg.attachments[0].url))

            is_boosting: bool = interaction.user in interaction.guild.premium_subscribers

            await self.db.current_submissions.insert_one(
                {
                    "user_ID": int(interaction.user.id),
                    "thread_ID": int(new_thread.id),
                    "submission_URL": edited_url,
                    "has_priority": is_boosting,
                    "time_added": int(datetime.now().strftime('%H%M%S')),
                    "thread_title": thread_name,
                    "thread_message_ID": int(thread_msg.id)
                }
            )

            await FeedbackQueueView().enable_buttons(new_thread, thread_msg.id)

            # Submission received - decrement slot counter
            await self.db.information.update_one(
                {"slots": refresh_data["slots"]},
                {"$inc": {"slots": -1}}
            )

            await self.refresh_button_state(interaction, False)
            await new_thread.send(content=f"New URL is {edited_url}")

    @discord.ui.button(label=f"Slots remaining: [awaiting DB update]",
                       style=discord.ButtonStyle.grey,
                       custom_id="slot_counter_button",
                       emoji="<:Discord_Members:1140057180482044025>",
                       disabled=True)
    async def slot_button(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer()
        await interaction.followup.send(content=f"This shouldn't happen", ephemeral=True)


class Events(commands.Cog):
    def __init__(self, bot):
        # Variables to pre-load
        self.event_stream = None
        self.event_stage = None
        self.event_chat = None
        self.vc_channel = None
        self.online_role = None
        self.event_type = None  # 0 = Stage; 1 = Stream

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)

        self.bot = bot

        # DB Setup
        self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("DEV_MONGO_URI"))
        self.db = self.client["_events"]

    async def cog_load(self):
        self.logger.info(f"Events.cog: LOADED!")

    @commands.Cog.listener()
    async def on_thread_delete(self, thread):
        # Locate submission's ObjectID and delete record in DB
        key = {"thread_ID": thread.id}

        # Search and delete submission record in DB
        async for result in self.db.current_submissions.find(key):
            delete_key = {"_id": result["_id"]}
            await self.db.current_submissions.delete_one(delete_key)
            print(str(f"Deleted submission record for {thread.name} ObjectID:{result['_id']}"))
            self.logger.info(f"Events.cog: {thread.name} - _events.current_submissions DB entry has been deleted.")

        # Search and delete feedback queue record in DB - If any
        async for result in self.db.feedback_queue.find(key):
            delete_key = {"_id": result["_id"]}
            await self.db.feedback_queue.delete_one(delete_key)
            print(str(f"Deleted feedback queue record for {thread.name} ObjectID:{result['_id']}"))
            self.logger.info(f"Events.cog: {thread.name} - _events.feedback_queue DB entry has been deleted.")

        self.logger.info(f"Events.cog: {thread.name} - thread has been deleted.")

    # FEEDBACK QUEUE COMMAND
    @app_commands.command(name="feedback_queue", description="Shows the current Feedback Queue™")
    @app_commands.checks.has_role("Event Host")
    async def display_feedback_queue(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(content="Generating the Feedback Queue™ now...", ephemeral=True)
        response_msg: discord.Message = await interaction.channel.send("<a:Combined_Load:1131251697734389910>")

        # Search DB record for submit message
        key = {"channel_ID": interaction.channel.id}
        search_result = None
        async for result in self.db.information.find(key):
            search_result = result

        feedback_queue_updated = {
            "$set": {
                "message_ID": response_msg.id,
                "channel_ID": interaction.channel.id,
                "last_user_ID": interaction.user.id,
                "slots": search_result["slots"],
                "submission_locator": "here i am"
            }
        }

        db_filter = {"submission_locator": "here i am"}  # Filter by userID
        await self.db.information.update_one(db_filter, feedback_queue_updated)

        await FeedbackQueueView().sort_feedback_queue(interaction, True)

    # PLAY TRACKS FROM FEEDBACK QUEUE
    @app_commands.command(name="track", description="Play a track in the Feedback Queue™")
    @app_commands.checks.has_role("Event Host")
    @app_commands.choices(mode=[
        app_commands.Choice(name="play", value=1),
        app_commands.Choice(name="move", value=2)
    ])
    async def feedback_queue_player(self, interaction: discord.Interaction,
                                    mode: app_commands.Choice[int], queue_pos: int, new_queue_pos: int | None):
        # PLAY mode - Select track from QUEUE_POS
        await interaction.response.defer()
        if mode.value == 1:
            queue_pos -= 1  # Remove 1 for list reasons
            sorted_q: list = await FeedbackQueueView().sort_feedback_queue(interaction, False)
            print(sorted_q)
            for i in range(0, len(sorted_q)):
                self.logger.info(f"Events.cog: {sorted_q[i]['track_user']} {sorted_q[i]['track_URL']}")

            q_user: discord.User = self.bot.get_user(int(sorted_q[queue_pos]["track_user_ID"]))
            q_next_url: str | None = sorted_q[queue_pos]["track_URL"]

            self.logger.error(sorted_q[queue_pos]["track_done"])

            if sorted_q[queue_pos]["track_done"]:  # Track has been played before - toggle undone
                update_q_state = {"$set": {"track_done": False}}
            else:
                update_q_state = {"$set": {"track_done": True}}

            update_q_filter = {"track_thread_ID": sorted_q[queue_pos]["track_thread_ID"]}  # Filter by thread ID
            await self.db.feedback_queue.update_one(update_q_filter, update_q_state, upsert=False)

            await FeedbackQueueView().sort_feedback_queue(interaction, True)  # Update new Feedback Queue state

            # Search for user's social links
            key = {"discord_user_ID": q_user.id}
            next_soundcloud: str = ""
            next_bandcamp: str = ""
            next_other: str = ""
            async for result in self.client["_server"].members.find(key):
                next_soundcloud = result["soundcloud_url"]
                next_bandcamp = result["bandcamp_url"]
                next_other = result["other_url"]

            # Send play message for bot
            if q_next_url is not None:  # URL is available to play - Update queue
                if not sorted_q[queue_pos]["track_done"]:  # Track hasn't been played yet - continue
                    await interaction.edit_original_response(content=f"DONE")
                    await interaction.channel.send(f";play {q_next_url}", delete_after=1)
                    if next_soundcloud == "" and next_bandcamp == "" and next_other == "":
                        await interaction.channel.send(f"### <:Discord_System_MessageWarn:1140060019044401154>"
                                                       f" No social links found for {q_user.display_name} :(\n### "
                                                       f"<:Discord_Support:1140060014820720703> <@{q_user.id}> "
                                                       f"You can setup your SoundCloud _`AND/OR`_ Bandcamp links using"
                                                       f" the **`/socials`** command!")
                    else:
                        await interaction.channel.send(f"{next_soundcloud}\n{next_bandcamp}\n{next_other}")
            else:  # No URL available to play - Alert
                await interaction.channel.send(
                    f"{q_user.display_name} has no URL - <@{os.getenv('HURLEY_ID')}>: DB ERROR!")
                self.logger.warning(f"Events.cog: No URL found for {q_user.display_name}'s submission in DB")

        # MOVE mode - Choose track from QUEUE_POS and move into NEW_QUEUE_POS
        elif mode.value == 2:
            queue_pos -= 1  # Remove 1 for list reasons
            new_queue_pos -= 1

            sorted_q: list = await FeedbackQueueView().sort_feedback_queue(interaction, False)
            print(sorted_q)

            updated_q = sorted_q

            check_for_same_place = False
            for i in range(0, len(updated_q)):
                try:
                    if updated_q[i]['queue_slot'] == new_queue_pos:  # New slot already taken
                        updated_q[i]['queue_slot'] += 1
                except KeyError:  # No queue_pos entry
                    continue
            for i in range(0, len(updated_q)):  # Fix remaining slots, if any
                if i == queue_pos:  # Same as old queue pos -> Change to new queue pos
                    updated_q[i]['queue_slot'] = new_queue_pos
                else:
                    try:
                        if updated_q[i]['queue_slot'] == updated_q[i + 1]['queue_slot']:
                            updated_q[i + 1]['queue_slot'] += 1
                    except KeyError:
                        continue

            print(updated_q)
            await self.db.feedback_queue.delete_many({})
            for i in range(0, len(updated_q)):
                await self.db.feedback_queue.insert_one(updated_q[i])

            await FeedbackQueueView().sort_feedback_queue(interaction, True)  # Update new Feedback Queue state

            self.logger.info(f"Events.cog: Moving track from {sorted_q[i]['track_user']} "
                             f"'{sorted_q[i]['track_URL']}' into position {new_queue_pos + 1} in the queue.")
            await interaction.edit_original_response(content="DONE")

    # EVENT HOST ONLY
    @app_commands.command(name="submit_system", description="Send the message with the button for submitting threads.")
    @app_commands.checks.has_role("Event Host")
    async def submission_button_ting(self, interaction: discord.Interaction,
                                     slot_amount: int):
        await interaction.response.defer()
        await interaction.followup.send(content=f"Setting up queue system with {slot_amount} slots...", ephemeral=True)
        response_msg: discord.Message = await interaction.channel.send("<a:Combined_Load:1131251697734389910>")

        event_submission_updated = {
            "$set": {
                "message_ID": response_msg.id,
                "channel_ID": interaction.channel.id,
                "last_user_ID": interaction.user.id,
                "slots": slot_amount,
                "submission_locator": "here i am"
            }
        }

        db_filter = {"submission_locator": "here i am"}  # Filter by userID
        await self.db.information.update_one(db_filter, event_submission_updated)

        await response_msg.edit(content="test", view=SubmitView(interaction))

    @staticmethod
    async def clean_thread(thread: discord.Thread):
        # Clean up and freeze channel for deletion
        await thread.edit(name="X")
        current_unix = int(time.time() + 31)

        await thread.send(
            content=f"## Cleaning up event material :: Deleting thread channel\n\n"
                    f"### <:Discord_Timeout:1140060025876922482> This message will expire <t:{current_unix}:R>"
        )

        await asyncio.sleep(30)
        await thread.delete()

    # EVENT MODE TOGGLE
    @app_commands.command(name="event", description="Sets Event Mode on and off.")
    @app_commands.checks.has_role("Event Host")
    @app_commands.choices(event_type=[
        discord.app_commands.Choice(name="Stage", value=0),
        discord.app_commands.Choice(name="Stream", value=1)
    ]
    )
    async def event(self, interaction: discord.Interaction,
                    event_type: discord.app_commands.Choice[int],
                    enable: bool):
        await interaction.response.defer()
        self.event_stage = self.bot.get_channel(int(os.getenv("DEV_EVENT_STAGE_ID")))
        self.event_stream = self.bot.get_channel(int(os.getenv("DEV_EVENT_STREAM_ID")))
        self.event_chat = self.bot.get_channel(int(os.getenv("DEV_EVENT_CHAT_ID")))

        self.online_role = discord.utils.get(interaction.guild.roles, name="Online")
        # Set permissions
        if event_type.value == 0:  # STAGE
            await self.event_stage.set_permissions(self.online_role, connect=enable)
            await self.event_chat.set_permissions(self.online_role, send_messages=enable)
            await interaction.followup.send(content=f"Event {event_type.name} mode is now set to '{str(enable)}'")

        # STREAM
        elif event_type.value == 1:
            await self.event_stream.set_permissions(self.online_role, connect=enable)
            await self.event_chat.set_permissions(self.online_role, send_messages=enable)
            await interaction.followup.send(content=f"Event {event_type.name} mode is now set to '{str(enable)}'")
            pass

        # I have no idea what would cause this so covering for the worst scenario
        else:
            await interaction.followup.send(content=f"Something broke in [event] logic.")
            pass

        if not enable:  # Cleanup event
            '''
                Goal: Delete all event-related threads and database entries

                Scan through current_submissions and start deletion
                Purge feedback_queue
            '''
            threads_to_delete = []
            async for result in self.db.current_submissions.find({}):
                print(result)
                current_thread_id = result["thread_ID"]

                thread_object: discord.Thread = interaction.client.get_channel(current_thread_id)

                threads_to_delete.append(thread_object)

            tasks = [asyncio.create_task(self.clean_thread(thread)) for thread in threads_to_delete]
            await asyncio.gather(*tasks)

            await self.client["_events"].current_submissions.delete_many({})  # Delete DB
            await self.client["_events"].feedback_queue.delete_many({})  # Delete DB
            await FeedbackQueueView().sort_feedback_queue(interaction, True)

        await interaction.followup.send(content=f"Event {event_type.name} mode is now set to '{str(enable)}'")
        pass

    # MOVE EVENT MEMBERS TO VC
    # TODO: Add option to move to any other VC (ideal for Stage <-> Stream)
    @app_commands.command(name="emove", description="Moves all members to #Hangout Room VC")
    @app_commands.checks.has_role("Event Host")
    async def eventmove(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.vc_channel = self.bot.get_channel(int(os.getenv("DEV_PUBLIC_VC_ID")))
        self.event_stage = self.bot.get_channel(int(os.getenv("DEV_EVENT_STAGE_ID")))
        self.event_stream = self.bot.get_channel(int(os.getenv("DEV_EVENT_STREAM_ID")))
        for member in self.event_stream.members:  # Move all #Event Stream to #Hangout Room
            await member.move_to(self.vc_channel)
        for member in self.event_stage.members:  # Move all #Event Stage to #Hangout Room
            await member.move_to(self.vc_channel)
        await interaction.followup.send(content=f"Moved all members to <#{self.vc_channel}>!")

    # GET EVENT MEMBER COUNT
    @app_commands.command(name="ecount", description="Counts all members in the event")
    @app_commands.checks.has_role("Event Host")
    async def eventsize(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.event_stream = self.bot.get_channel(int(os.getenv("DEV_EVENT_STREAM_ID")))
        self.event_stage = self.bot.get_channel(int(os.getenv("DEV_EVENT_STAGE_ID")))
        await interaction.followup.send(content=f"There are {str(len(self.event_stream.members))} "
                                                f"people in the stream!")

    # ** ONLY
    # @app_commands.default_permissions(moderate_members=True)
    # @app_commands.checks.has_permissions(moderate_members=True)
    # @app_commands.command(name="random", description="Picks a random reacted user from message")
    # async def randomreact(self, interaction: discord.Interaction, msg: discord.InteractionMessage):
    #     users = msg.reactions[0].users().flatten()
    #     print(users)
    #     winner = random.choice(users)
    #     print(winner)
    #     await interaction.response.send_message(f'{winner.mention} is the lucky winner!')


async def setup(bot):
    await bot.add_cog(Events(bot))
